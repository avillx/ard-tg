import logging
import os

import telebot

import agent
import arch_agent.client as client
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

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("app")

    # app building
    bot = telebot.TeleBot(
        token                 = telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    # set up logging
    bot.setup_middleware(tg_utils.LoggingMiddleware(logger))

    agent_client = client.Client(
        base_url = agent_url
    )

    session_service = agent.SessionService(
        agent_id     = agent_id,
        agent_client = agent_client,
        life_time    = float(session_life_time)
    )

    agent_service = agent.AgentService(
        agent_url       = agent_url,
        agent_client    = agent_client,
        agent_id        = agent_id,
        session_service = session_service
    )

    # set handlers
    handlers = tg_handlers.Handlers(
        agent_service  = agent_service,
        sticker_pack   = sticker_pack,
        sticker_chache = tg_utils.StickerChache(bot,logger),
    )
    handlers.register_on(bot)

    # white list middle wate
    if allowed_chats_raw != "":
        allowed_chat_ids : list[int] = [int(x) for x in allowed_chats_raw.split(",")]
        bot.setup_middleware(tg_utils.UserWhitelistMiddleware(allowed_chat_ids,logger))

    # bot start
    if webhook_url != "":
        logger.info("start with webhook")
        tg_utils.run_bot_with_webhook(bot,webhook_url)
    else:
        logger.info("start with polling")
        bot.infinity_polling()


if __name__ == "__main__":
    main()
