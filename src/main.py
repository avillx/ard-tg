import dataclasses
import logging
import os
import sys
import urllib.parse as urlparse

import telebot

import agent
import ard.client as client
import attach
import contacts
import notifications
import server
import storage
import telegram


@dataclasses.dataclass(frozen=True, slots=True)
class Config:
    telegram_token: str
    agent_url: str
    agent_id: str
    session_life_time: str
    sticker_pack: str
    allowed_chats: list[int]
    webhook_url: str
    agent_datapath: str
    file_storage_path: str
    notify_chat_id: int | None

    def __post_init__(self) -> None:
        if self.agent_datapath == "":
            raise ValueError("'ARDTG_AGENT_DATAPATH' is required")

        if self.file_storage_path == "":
            raise ValueError("'ARDTG_FILESTORAGE_PATH' is required")

        if self.telegram_token == "":
            raise ValueError("'ARDTG_TELEGRAM_TOKEN' is required")

        if self.agent_url == "":
            raise ValueError("'ARDTG_AGENT_URL' is required")

        # validate url
        try:
            parsed = urlparse.urlparse(self.agent_url)
            _ = parsed.port  # raise ValueError on invalid port
        except ValueError as e:
            raise ValueError(f"'ARDTG_AGENT_URL' is invalid: '{self.agent_url}' ") from e

        if parsed.scheme not in ("http", "https"):
            raise ValueError("'ARDTG_AGENT_URL' must start with http or https scheme")


def load_config() -> Config:

    # cast and validate allowed chats
    allowed_chats: list[int] = []
    allowed_chats_raw: str = os.getenv("ARDTG_ALLOWED_CHATS", "")
    if allowed_chats_raw != "":
        for allowed_chat_id in allowed_chats_raw.split(","):
            try:
                allowed_chats.append(int(allowed_chat_id))
            except ValueError as e:
                raise ValueError("'ARDTG_NOTIFY_CHAT_ID' must be a chat id") from e

    # cast and validate notify ChatID
    notify_chat_id: int | None = None
    notify_chat_id_raw: str = os.getenv("ARDTG_NOTIFY_CHAT_ID", "")
    if notify_chat_id_raw != "":
        try:
            notify_chat_id = int(notify_chat_id_raw)
        except ValueError as e:
            raise ValueError("'ARDTG_NOTIFY_CHAT_ID' must be a chat id") from e

    return Config(
        telegram_token=os.getenv("ARDTG_TELEGRAM_TOKEN", ""),
        agent_url=os.getenv("ARDTG_AGENT_URL", ""),
        agent_id=os.getenv("ARDTG_AGENT_ID", "default"),
        session_life_time=os.getenv("ARDTG_SESSION_LIFE_TIME", "600"),
        sticker_pack=os.getenv("ARDTG_STICKER_PACK", ""),
        webhook_url=os.getenv("ARDTG_WEBHOOK_URL", ""),
        agent_datapath=os.getenv("ARDTG_AGENT_DATAPATH", ""),
        file_storage_path=os.getenv("ARDTG_FILESTORAGE_PATH", ""),
        allowed_chats=allowed_chats,
        notify_chat_id=notify_chat_id,
    )


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("App")


# fmt: off
def build_app(cfg: Config,logger: logging.Logger) -> server.BotServer:

    bot = telebot.TeleBot(
        token                 = cfg.telegram_token,
        parse_mode            = "MarkdownV2",
        num_threads           = 4,
        use_class_middlewares = True,
    )

    # set up logging
    bot.setup_middleware(telegram.LoggingMiddleware(
        logger = logger,
    ))

    contacts_storage = storage.FileStorage(
        logger       = logger,
        storage_path = cfg.file_storage_path,
    )

    contact_service = contacts.ContactService(
        logger       = logger,
        storage      = contacts_storage,
    )

    bot.setup_middleware(telegram.UserContactKeeper(
        contact_service = contact_service,
    ))

    if cfg.allowed_chats != "":
        bot.setup_middleware(telegram.UserWhitelistMiddleware(
            allowed_chats = cfg.allowed_chats,
            logger        = logger,
        ))

    agent_client = client.Client(
        base_url = cfg.agent_url
    )

    session_service = agent.SessionService(
        agent_id     = cfg.agent_id,
        agent_client = agent_client,
        life_time    = float(cfg.session_life_time),
        logger       = logger,
        instruction  = telegram._TELEGRAM_GUIDE,
        time         = agent.SystemTime(),
    )

    agent_service = agent.Service(
        agent_url       = cfg.agent_url,
        agent_client    = agent_client,
        agent_id        = cfg.agent_id,
        session_service = session_service,
        logger          = logger,
    )

    user_attachments_storage = storage.FileStorage(
        logger       = logger,
        storage_path = os.path.join(cfg.agent_datapath,"tmp"),
    )

    telegram_service = telegram.Service(
        agent_service   = agent_service,
        sticker_pack    = cfg.sticker_pack,
        storage_        = user_attachments_storage,
        sticker_cache   = telegram.StickerCache(bot,logger),
        session_service = session_service,
        notify_chat_id  = cfg.notify_chat_id,
        logger          = logger,
    )
    telegram_service.set_commands_prompt(bot)
    telegram_service.register_on(bot)

    attachment_service  = attach.AttachService(
        bot             = bot,
        session_service = session_service,
        logger          = logger,
    )

    notifier_svc = notifications.PlaceholderNotifier(logger)
    if isinstance(cfg.notify_chat_id,int):
        notifier_svc = notifications.TelegramNotifier(
            bot=bot,
            logger=logger,
            notify_chat_id=cfg.notify_chat_id,
        )

    return server.BotServer(
        attachment_service=attachment_service,
        contact_service=contact_service,
        logger=logger,
        notifier=notifier_svc,
        webhook_url=cfg.webhook_url,
    )

def main():
    logger = get_logger()

    try:
        config = load_config()
    except Exception as e:
        logger.fatal(f"Bad config: {e}")
        sys.exit(1)

    app = build_app(config,logger)

    app.run()

if __name__ == "__main__":
    main()
