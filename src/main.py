import logging
import os
import secrets
import sys

import telebot

import agent
import arch_agent.client as client
import attach
import contacts
import server
import telegram


def main():
    # fmt: off

    # envirement variables
    telegram_token    : str = os.getenv("TELEGRAM_TOKEN","")
    agent_url         : str = os.getenv("AGENT_URL","")
    agent_id          : str = os.getenv("AGENT_ID","default")
    session_life_time : str = os.getenv("SESSION_LIFE_TIME","600")
    sticker_pack      : str = os.getenv("STICKER_PACK","")
    allowed_chats_raw : str = os.getenv("ALLOWED_CHATS","")
    webhook_url       : str = os.getenv("WEBHOOK_URL","")
    storage_path      : str = os.getenv("STORAGE_PATH","")

    logger = logging.getLogger("App")
    logging.basicConfig(
        level   = logging.INFO,
        format  = "[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
    )

    if telegram_token == "":
        logger.fatal("'TELEGRAM_TOKEN' is required")
        sys.exit(1)

    if agent_url == "":
        logger.fatal("'AGENT_URL' is required")
        sys.exit(1)

    # app building
    bot = telebot.TeleBot(
        token                 = telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    # set up logging
    bot.setup_middleware(telegram.LoggingMiddleware(
        logger = logger,
    ))


    contact_service = contacts.ContactService(
        logger       = logger,
        storage_path = storage_path
    )

    bot.setup_middleware(telegram.UserContactKeeper(
        contact_service = contact_service,
    ))

    if allowed_chats_raw != "":
        bot.setup_middleware(telegram.UserWhitelistMiddleware(
            allowed_chats = [int(x) for x in allowed_chats_raw.split(",")],
            logger        = logger,
        ))

    agent_client = client.Client(
        base_url = agent_url
    )

    session_service = agent.SessionService(
        agent_id     = agent_id,
        agent_client = agent_client,
        life_time    = float(session_life_time),
        logger       = logger,
        instruction  = telegram._TELEGRAM_GUIDE
    )

    agent_service = agent.Service(
        agent_url       = agent_url,
        agent_client    = agent_client,
        agent_id        = agent_id,
        session_service = session_service,
        logger          = logger,
    )

    telegram_svc = telegram.Service(
        agent_service   = agent_service,
        sticker_pack    = sticker_pack,
        file_storage    = storage_path,
        sticker_cache   = telegram.StickerCache(bot,logger),
        session_service = session_service,
        logger          = logger,
    )
    telegram_svc.set_commands_prompt(bot)
    telegram_svc.register_on(bot)

    attachment_service  = attach.AttachService(
        bot             = bot,
        session_service = session_service,
        logger          = logger,
    )

    # build server
    post_routes : dict[str, server.EndpointHandler] = {
        "/attach" : server.AttachSessionHandler(attachment_service)
    }

    if webhook_url != "":
        webhook_path = f"/bot/{secrets.token_hex(16)}"
        post_routes[webhook_path] = server.bot_webhook_handler(bot,webhook_url,webhook_path)

    srv = server.build_server(
        get_routes  = {"/contacts" : server.ContactsHandler(contact_service)},
        post_routes = post_routes,
        logger      = logger,
    )

    if webhook_url != "":
        logger.info("run with webhook")
        srv.serve_forever()
    else:
        logger.info("run with polling")
        server.serve_with_polling(bot,srv,logger)


if __name__ == "__main__":
    main()
