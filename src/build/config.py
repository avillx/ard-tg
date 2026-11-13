import dataclasses
import os
import urllib.parse as urlparse
lazy from collections.abc import Callable

import agent


def _env_value[ValueT](
    name: str, parse: Callable[[str], ValueT], default: ValueT, expected: str
) -> ValueT:
    """Read `name` from the environment and parse it, or return `default` when it is unset."""
    raw = os.getenv(name, "")
    if raw == "":
        return default
    try:
        return parse(raw)
    except ValueError as e:
        raise ValueError(f"'{name}' must be {expected}") from e


def _parse_chat_ids(raw: str) -> list[int]:
    return [int(chat_id) for chat_id in raw.split(",")]


def _env_value_session_ttl() -> float:
    return _env_value("ARDTG_SESSION_LIFE_TIME", float, agent._DEFAULT_SESSION_TTL, "a number")


@dataclasses.dataclass(frozen=True, slots=True)
class Config:
    telegram_token: str = os.getenv("ARDTG_TELEGRAM_TOKEN", "")
    agent_url: str = os.getenv("ARDTG_AGENT_URL", "")
    agent_id: str = os.getenv("ARDTG_AGENT_ID", "default")
    sticker_pack: str = os.getenv("ARDTG_STICKER_PACK", "")
    webhook_url: str = os.getenv("ARDTG_WEBHOOK_URL", "")
    agent_datapath: str = os.getenv("ARDTG_AGENT_DATAPATH", "")
    file_storage_path: str = os.getenv("ARDTG_FILESTORAGE_PATH", "")
    notify_chat_id: int | None = _env_value("ARDTG_NOTIFY_CHAT_ID", int, None, "a chat id")
    allowed_chats: list[int] = dataclasses.field(
        default_factory=lambda: _env_value("ARDTG_ALLOWED_CHATS", _parse_chat_ids, [], "a chat id")
    )
    session_life_time: float = _env_value_session_ttl()

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
