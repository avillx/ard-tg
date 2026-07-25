import os

import telebot

import api_bindings.arch_agent_api_client.client as client
import telegram as tg
from agent import AgentService, SessionService


def main():
    # fmt: off
    telegram_token    : str = os.getenv("TELEGRAM_TOKEN")
    agent_url         : str = os.getenv("AGENT_URL")
    agent_id          : str = os.getenv("AGENT_ID")
    session_life_time : str = os.getenv("SESSION_LIFE_TIME")
    sticker_pack      : str = os.getenv("STICKER_PACK")
    allowed_chats_raw : str = os.getenv("ALLOWED_CHATS","")
    webhook_url       : str = os.getenv("WEBHOOK_URL","")

    bot = telebot.TeleBot(
        token                 = telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    agent_client = client.Client(
        base_url = agent_url
    )

    session_service = SessionService(
        agent_id     = agent_id,
        agent_client = agent_client,
        life_time    = float(session_life_time)
    )

    agent_service = AgentService(
        agent_url       = agent_url,
        agent_client    = agent_client,
        agent_id        = agent_id,
        session_service = session_service
    )

    handlers = tg.Handlers(
        agent_service  = agent_service,
        sticker_pack   = sticker_pack,
        sticker_chache = tg.StickerChache(bot=bot),
    )
    handlers.register_on(bot)

    if allowed_chats_raw != "":
        allowed_chat_ids : list[int] = [int(x) for x in allowed_chats_raw.split(",")]
        bot.setup_middleware(tg.UserWhitelistMiddleware(allowed_chat_ids))

    if webhook_url != "":
        tg.run_bot_with_webhook(bot,webhook_url)
    else:
        bot.infinity_polling()


if __name__ == "__main__":
    main()

