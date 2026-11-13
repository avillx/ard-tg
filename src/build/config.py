import dataclasses
import os
import urllib.parse as urlparse

import agent


def _get_allowed_chats() -> list[int]:
    allowed_chats: list[int] = []
    allowed_chats_raw: str = os.getenv("ARDTG_ALLOWED_CHATS", "")
    if allowed_chats_raw != "":
        for allowed_chat_id in allowed_chats_raw.split(","):
            try:
                allowed_chats.append(int(allowed_chat_id))
            except ValueError as e:
                raise ValueError("'ARDTG_ALLOWED_CHATS' must be a chat id") from e
    return allowed_chats


def _get_notify_chat_id() -> int | None:
    notify_chat_id: int | None = None
    notify_chat_id_raw: str = os.getenv("ARDTG_NOTIFY_CHAT_ID", "")
    if notify_chat_id_raw != "":
        try:
            notify_chat_id = int(notify_chat_id_raw)
        except ValueError as e:
            raise ValueError("'ARDTG_NOTIFY_CHAT_ID' must be a chat id") from e

    return notify_chat_id


def _get_session_life_time() -> float:
    session_life_time: float = agent._DEFAULT_SESSION_TTL
    session_life_time_raw = os.getenv("ARDTG_SESSION_LIFE_TIME", "")
    if session_life_time_raw == "":
        try:
            session_life_time = float(session_life_time_raw)
        except ValueError as e:
            raise ValueError("'ARDTG_SESSION_LIFE_TIME' must be a number") from e
    return session_life_time


@dataclasses.dataclass(frozen=True, slots=True)
class Config:
    telegram_token: str = os.getenv("ARDTG_TELEGRAM_TOKEN", "")
    agent_url: str = os.getenv("ARDTG_AGENT_URL", "")
    agent_id: str = os.getenv("ARDTG_AGENT_ID", "default")
    sticker_pack: str = os.getenv("ARDTG_STICKER_PACK", "")
    webhook_url: str = os.getenv("ARDTG_WEBHOOK_URL", "")
    agent_datapath: str = os.getenv("ARDTG_AGENT_DATAPATH", "")
    file_storage_path: str = os.getenv("ARDTG_FILESTORAGE_PATH", "")
    notify_chat_id: int | None = _get_notify_chat_id()
    session_life_time: float = _get_session_life_time()
    allowed_chats: list[int] = dataclasses.field(default_factory=_get_allowed_chats)

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
