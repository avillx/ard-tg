import os
import urllib.parse as urlparse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ardtg.domain.session import DEFAULT_SESSION_TTL

if TYPE_CHECKING:
    from collections.abc import Callable

class ConfigError(ValueError):
    pass

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
        raise ConfigError(f"'{name}' must be {expected}") from e


def _parse_chat_ids(raw: str) -> list[int]:
    return [int(chat_id) for chat_id in raw.split(",")]


def _env_value_session_ttl() -> float:
    return _env_value("ARDTG_SESSION_LIFE_TIME", float, DEFAULT_SESSION_TTL, "a number")

def _optional_env(name: str) -> str:
    return os.getenv(name, "")

def _required_env(name: str) -> str:
    value = os.getenv(name, "")
    if value == "":
        raise ConfigError(f"'{name}' is required")
    return value

def _validate_url(url: str):
    try:
        parsed = urlparse.urlparse(url)
        _ = parsed.port  # raise ValueError on invalid port
    except ValueError as err:
        raise ConfigError(f"config has invalid url: '{url}' ") from err

    if parsed.scheme not in ("http", "https"):
        raise ConfigError(f"config has invalid url: '{url}'. must start with http or https scheme")


def _requred_url(name:str) -> str:
    url = _required_env(name)
    _validate_url(name)
    return url

def _optional_url(name:str) -> str:
    url = _optional_env(name)
    if url != "":
        _validate_url(name)
    return url

# # TODO:
# def _required_path

@dataclass(frozen=True, slots=True)
class Config:

    # required envs
    telegram_token: str = _required_env("ARDTG_TELEGRAM_TOKEN")
    agent_url: str = _requred_url("ARDTG_AGENT_URL")
    agent_datapath: str = _required_env("ARDTG_AGENT_DATAPATH")
    file_storage_path: str = _required_env("ARDTG_FILESTORAGE_PATH")

    # optional envs
    webhook_url: str = _optional_url("ARDTG_WEBHOOK_URL")
    sticker_pack: str = _optional_env("ARDTG_STICKER_PACK")

    # typed envs
    notify_chat_id: int | None = _env_value("ARDTG_NOTIFY_CHAT_ID", int, None, "a chat id")
    allowed_chats: list[int] = field(
        default_factory=lambda: _env_value("ARDTG_ALLOWED_CHATS", _parse_chat_ids, [], "a chat id")
    )
    session_life_time: float = _env_value_session_ttl()
