import logging
import os

import telebot

import agent
import arch_agent.client as client
import middleware
import session
import telegram_handlers as tg_handlers
import telegram_utils as tg_utils


def main():
    # fmt: off

    # envirement variables
    telegram_token    : str = os.getenv("TELEGRAM_TOKEN")
    agent_url         : str = os.getenv("AGENT_URL")
    agent_id          : str = os.getenv("AGENT_ID")
    session_life_time : str = os.getenv("SESSION_LIFE_TIME","600")
    sticker_pack      : str = os.getenv("STICKER_PACK","")
    allowed_chats_raw : str = os.getenv("ALLOWED_CHATS","")
    webhook_url       : str = os.getenv("WEBHOOK_URL","")
    storage_path      : str = os.getenv("STORAGE_PATH","")

    logger = logging.getLogger("App")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # app building
    bot = telebot.TeleBot(
        token                 = telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    # set up logging
    bot.setup_middleware(middleware.LoggingMiddleware(logger))

    agent_client = client.Client(
        base_url = agent_url
    )

    session_service = session.SessionService(
        agent_id     = agent_id,
        agent_client = agent_client,
        life_time    = float(session_life_time),
        logger       = logger,
        instruction  = tg_utils._TELEGRAM_GUIDE
    )

    agent_service = agent.AgentService(
        agent_url       = agent_url,
        agent_client    = agent_client,
        agent_id        = agent_id,
        session_service = session_service,
        logger          = logger,
    )

    handlers = tg_handlers.Handlers(
        agent_service  = agent_service,
        sticker_pack   = sticker_pack,
        file_storage   = storage_path,
        sticker_chache = tg_utils.StickerChache(bot,logger),
        logger=logger,
    )
    handlers.set_commands_prompt(bot)
    handlers.register_on(bot)

    # white list middleware
    if allowed_chats_raw != "":
        allowed_chat_ids : list[int] = [int(x) for x in allowed_chats_raw.split(",")]
        white_list_middle_ware = middleware.UserWhitelistMiddleware(
            allowed_chats = allowed_chat_ids,
            logger        = logger,
        )
        bot.setup_middleware(white_list_middle_ware)

    # bot start
    if webhook_url != "":
        logger.warning("start with webhook")
        tg_utils.run_bot_with_webhook(bot,webhook_url)
    else:
        logger.warning("start with polling")
        bot.infinity_polling()


if __name__ == "__main__":
    main()
