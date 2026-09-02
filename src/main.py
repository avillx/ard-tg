import logging
import os
import secrets

import telebot

import agent
import arch_agent.client as client
import attach
import middleware
import server
import session
import telegram_handlers as tg_handlers
import telegram_utils as tg_utils

import contacts

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
        level   = logging.INFO,
        format  = "[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
    )

    # app building
    bot = telebot.TeleBot(
        token                 = telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    # set up logging
    bot.setup_middleware(middleware.LoggingMiddleware(
        logger = logger,
    ))


    contact_service = contacts.ContactService(
        logger    = logger,
        file_path = storage_path
    )

    bot.setup_middleware(middleware.UserContactKeeper(
        contact_service = contact_service,
    ))

    if allowed_chats_raw != "":
        bot.setup_middleware(middleware.UserWhitelistMiddleware(
            allowed_chats = [int(x) for x in allowed_chats_raw.split(",")],
            logger        = logger,
        ))

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
        agent_service   = agent_service,
        sticker_pack    = sticker_pack,
        file_storage    = os.path.join(storage_path,"uploads"),
        sticker_chache  = tg_utils.StickerChache(bot,logger),
        session_service = session_service,
        logger          = logger,
    )
    handlers.set_commands_prompt(bot)
    handlers.register_on(bot)

    attachment_service  = attach.AttachService(
        bot             = bot,
        session_service = session_service,
        logger          = logger,
    )

    # build server
    post_routes = {
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
