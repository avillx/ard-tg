import logging
from pathlib import Path

import telebot

import agent
import ard.client as client
import attach
import contacts
import notifications
import server
import storage
import telegram
lazy import build


def bot_server(cfg: build.Config) -> server.BotServer:

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

    proifle_service = agent.ProfileService(
        agent_client=agent_client,
    )

    session_service = agent.SessionService(
        agent_client=agent_client,
        life_time=float(cfg.session_life_time),
        logger=logger,
        instruction=telegram.TELEGRAM_GUIDE,
        time=agent.SystemTime(),
        profile_source=proifle_service,
    )

    agent_service = agent.Service(
        agent_url=cfg.agent_url,
        agent_client=agent_client,
        session_service=session_service,
        logger=logger,
    )

    user_attachments_storage = storage.FileStorage(
        logger=logger,
        storage_path=str(Path(cfg.agent_datapath) / "tmp"),
    )

    telegram_handlers: list[telegram.BasicHandler] = [
        telegram.InterruptHandler(
            agent_service=agent_service,
        ),
        telegram.TasksHandler(
            agent_service=agent_service,
        ),
        telegram.MCPHandler(
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
        telegram.ShowProfileHandler(
            profile_service=proifle_service,
        ),
        telegram.SetProfileHandler(
            profile_service=proifle_service,
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

    # TODO: this should be runtime operaions
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
