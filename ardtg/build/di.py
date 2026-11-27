import logging
from pathlib import Path
from typing import TYPE_CHECKING

import telebot

from ardtg.ard_api import Client
from ardtg.ard_api_adapter.activity import AgentAPIActivityRepo
from ardtg.ard_api_adapter.chat import AgentAPIChatStreamer
from ardtg.ard_api_adapter.consolidaton import AgentAPIConsolidationAdapter
from ardtg.ard_api_adapter.interruption import AgentAPIInterruption
from ardtg.ard_api_adapter.mcp import AgentAPIMCPListAdapter
from ardtg.ard_api_adapter.profile import AgentAPIProfileAdapter
from ardtg.ard_api_adapter.session import AgentAPINewSession
from ardtg.ard_api_adapter.task import AgentAPITaskListAdapter
from ardtg.ard_api_adapter.tool import AgentAPIResultSink
from ardtg.build.app import BotApp
from ardtg.domain.activity import TodayActivity
from ardtg.domain.attach import AttachService
from ardtg.domain.chat import ChatService
from ardtg.domain.consolidation import ConsolidationService
from ardtg.domain.contacts import ContactService
from ardtg.domain.notifications import BotNotifier, PlaceholderNotifier
from ardtg.domain.profile import ProfileService
from ardtg.domain.session import SessionService, SystemTime
from ardtg.domain.tool import ProvidedToolExecutor
from ardtg.storage.contacts import ContactJSONStorage
from ardtg.storage.filestorage import FileStorage
from ardtg.telegram.handler_activity import ActivityHandler
from ardtg.telegram.handler_consolidation import ConsolidationHandler
from ardtg.telegram.handler_general_message import GeneralMessageHandler
from ardtg.telegram.handler_interrupt import InterruptHandler
from ardtg.telegram.handler_mcp import MCPHandler
from ardtg.telegram.handler_new_session import NewSessionHandler
from ardtg.telegram.handler_profile import SetProfileHandler, ShowProfileHandler
from ardtg.telegram.handler_tasks import TasksHandler
from ardtg.telegram.messanger_bot import TelegramMessangerBot
from ardtg.telegram.middleware import (
    LoggingMiddleware,
    UserContactKeeper,
    UserWhitelistMiddleware,
)
from ardtg.telegram.service import TELEGRAM_GUIDE, BasicHandler, TelegramService
from ardtg.telegram.stickers import StickerToolsFactory
from ardtg.telegram.tools import FSToolsFactory

if TYPE_CHECKING:
    from ardtg.build.config import Config
    from ardtg.telegram.handler_general_message import TelegramToolFactory


def build_app(cfg: Config) -> BotApp:

    logger = logging.getLogger("app")

    bot = telebot.TeleBot(
        token=cfg.telegram_token,
        parse_mode="MarkdownV2",
        num_threads=4,
        use_class_middlewares=True,
    )

    # set up logging
    bot.setup_middleware(
        LoggingMiddleware(
            logger=logger,
        )
    )

    contacts_file_storage = FileStorage(
        logger=logger,
        storage_path=cfg.file_storage_path,
    )

    contacts_json_storage = ContactJSONStorage(_storage=contacts_file_storage)

    contact_service = ContactService(
        repo=contacts_json_storage,
        logger=logger,
    )

    bot.setup_middleware(
        UserContactKeeper(
            contact_sink=contact_service,
        )
    )

    if len(cfg.allowed_chats) > 0:
        bot.setup_middleware(
            UserWhitelistMiddleware(
                allowed_chats=cfg.allowed_chats,
                logger=logger,
            )
        )

    agent_api_client = Client(base_url=cfg.agent_url)

    profile_repo = AgentAPIProfileAdapter(agent_client=agent_api_client)

    proifle_service = ProfileService(
        profile_repo=profile_repo,
    )

    session_repo = AgentAPINewSession(agent_client=agent_api_client)

    session_service = SessionService(
        profile_statement=proifle_service,
        life_time=cfg.session_life_time,
        instruction=TELEGRAM_GUIDE,
        logger=logger,
        session_creator=session_repo,
        time=SystemTime(),
    )

    user_attachments_storage = FileStorage(
        logger=logger,
        storage_path=str(Path(cfg.agent_datapath) / "tmp"),
    )

    interruptor = AgentAPIInterruption(
        client=agent_api_client,
        logger=logger,
    )

    interruption_handler = InterruptHandler(
        interruptor=interruptor,
        session_statement=session_service,
    )

    tasks_list = AgentAPITaskListAdapter(
        client=agent_api_client,
        logger=logger,
    )

    tasks_handler = TasksHandler(
        task_list_service=tasks_list,
    )

    mcp_repo = AgentAPIMCPListAdapter(
        client=agent_api_client,
        logger=logger,
    )

    mcp_handler = MCPHandler(
        mcp_repo=mcp_repo,
    )

    activity_repo = AgentAPIActivityRepo(client=agent_api_client, logger=logger)

    today_activity = TodayActivity(repo=activity_repo)

    activity_handler = ActivityHandler(
        today_activity=today_activity,
    )

    new_session_handler = NewSessionHandler(
        interruptor=interruptor,
        session_dropper=session_service,
        session_statement=session_service,
    )

    consolidation_streamer = AgentAPIConsolidationAdapter(
        client=agent_api_client,
        agent_url=cfg.agent_url,
    )

    consolidator = ConsolidationService(
        consolidation_streamer=consolidation_streamer,
        logger=logger,
    )

    consolidation_handler = ConsolidationHandler(
        consolidator=consolidator,
        logger=logger,
    )

    show_profile_handler = ShowProfileHandler(
        profile_source=profile_repo,
    )

    set_profile_handler = SetProfileHandler(
        profile_setter=proifle_service,
    )

    chat_streamer = AgentAPIChatStreamer(
        agent_client=agent_api_client,
        agent_url=cfg.agent_url,
        logger=logger,
    )

    tool_factories: list[TelegramToolFactory] = [FSToolsFactory()]
    if cfg.sticker_pack is not None:
        tool_factories.append(
            StickerToolsFactory(
                sticker_pack_name=cfg.sticker_pack,
                logger=logger,
            )
        )

    tool_call_sink = AgentAPIResultSink(client=agent_api_client, logger=logger)

    tool_executor = ProvidedToolExecutor(
        sink=tool_call_sink,
    )

    chat = ChatService(
        chat_streamer=chat_streamer,
        interruptor=interruptor,
        session_statement=session_service,
        logger=logger,
    )

    general_message_handler = GeneralMessageHandler(
        chat=chat,
        tool_factories=tool_factories,
        storage=user_attachments_storage,
        tool_executor=tool_executor,
        logger=logger,
    )

    telegram_handlers: list[BasicHandler] = [
        interruption_handler,
        tasks_handler,
        mcp_handler,
        activity_handler,
        new_session_handler,
        consolidation_handler,
        show_profile_handler,
        set_profile_handler,
        general_message_handler,
    ]

    telegram_service = TelegramService(
        handlers=telegram_handlers,
        bot=bot,
    )

    telegram_messanger_bot = TelegramMessangerBot(bot=bot)

    attachment_service = AttachService(
        messanger_bot=telegram_messanger_bot,
        session_definer=session_service,
        logger=logger,
    )

    notifier = PlaceholderNotifier(logger)
    if cfg.notify_chat_id is not None:
        notifier = BotNotifier(
            messanger_bot=telegram_messanger_bot,
            logger=logger,
            notify_chat_id=cfg.notify_chat_id,
        )

    return BotApp(
        attacher=attachment_service,
        contact_store=contact_service,
        telegram_service=telegram_service,
        notifier=notifier,
        webhook_url=cfg.webhook_url,
        bot=bot,
        logger=logger,
    )
