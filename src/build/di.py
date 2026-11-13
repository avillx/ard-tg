import logging
import os

import telebot

import agent
import ard.client as client
import attach
import contacts
import notifications
import server
import storage
import telegram
from build.config import Config


def bot_server(cfg: Config) -> server.BotServer:

    logger = logging.getLogger("app")

    bot = telebot.TeleBot(
        token=cfg.telegram_token,
        parse_mode="MarkdownV2",
        num_threads=4,
        use_class_middlewares=True,
    )

    # set up logging
    bot.setup_middleware(
        telegram.LoggingMiddleware(
            logger=logger,
        )
    )

    contacts_storage = storage.FileStorage(
        logger=logger,
        storage_path=cfg.file_storage_path,
    )

    contact_service = contacts.ContactService(
        logger=logger,
        storage=contacts_storage,
    )

    bot.setup_middleware(
        telegram.UserContactKeeper(
            contact_service=contact_service,
        )
    )

    if len(cfg.allowed_chats) > 0:
        bot.setup_middleware(
            telegram.UserWhitelistMiddleware(
                allowed_chats=cfg.allowed_chats,
                logger=logger,
            )
        )

    agent_client = client.Client(base_url=cfg.agent_url)

    session_service = agent.SessionService(
        agent_id=cfg.agent_id,
        agent_client=agent_client,
        life_time=float(cfg.session_life_time),
        logger=logger,
        instruction=telegram._TELEGRAM_GUIDE,
        time=agent.SystemTime(),
    )

    agent_service = agent.Service(
        agent_url=cfg.agent_url,
        agent_client=agent_client,
        agent_id=cfg.agent_id,
        session_service=session_service,
        logger=logger,
    )

    user_attachments_storage = storage.FileStorage(
        logger=logger,
        storage_path=os.path.join(cfg.agent_datapath, "tmp"),
    )

    telegram_handlers: list[telegram.Handler] = [
        telegram.InterruptHandler(
            agent_service=agent_service,
        ),
        telegram.ToolsHandler(
            agent_service=agent_service,
        ),
        telegram.TasksHandler(
            agent_service=agent_service,
        ),
        telegram.McpHandler(
            agent_service=agent_service,
        ),
        telegram.ActivityHandler(
            agent_service=agent_service,
        ),
        telegram.NewSessionHandler(
            agent_service=agent_service,
            session_service=session_service,
        ),
        telegram.ConsolidationHandler(
            agent_service=agent_service,
            logger=logger,
        ),
        # general message handler must be registered last, it captures all the rest
        telegram.GeneralMessageHandler(
            agent_service=agent_service,
            sticker_pack=cfg.sticker_pack,
            storage_=user_attachments_storage,
            sticker_cache=telegram.StickerCache(bot, logger),
            logger=logger,
        ),
    ]

    telegram_service = telegram.Service(
        handlers=telegram_handlers,
    )
    telegram_service.set_commands_prompt(bot)
    telegram_service.register_handlers(bot)

    attachment_service = attach.AttachService(
        bot=bot,
        session_service=session_service,
        logger=logger,
    )

    notifier_svc = notifications.PlaceholderNotifier(logger)
    if isinstance(cfg.notify_chat_id, int):
        notifier_svc = notifications.TelegramNotifier(
            bot=bot,
            logger=logger,
            notify_chat_id=cfg.notify_chat_id,
        )

    return server.BotServer(
        attachment_service=attachment_service,
        contact_service=contact_service,
        notifier=notifier_svc,
        webhook_url=cfg.webhook_url,
        bot=bot,
        logger=logger,
    )
