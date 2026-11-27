import urllib.parse as urlparse
from dataclasses import dataclass
from typing import TYPE_CHECKING

from telebot.util import validate_token

from ardtg.domain.session import DEFAULT_SESSION_TTL

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


class ConfigError(ValueError):
    pass


def _env_value[ValueT](
    name: str,
    caster: Callable[[str], ValueT],
    environ: Mapping[str, str],
) -> ValueT | None:
    """Read `name` from the environment and parse it, or return `default` when it is unset."""
    raw = environ.get(name)
    if raw is None:
        return None
    try:
        return caster(raw)
    except ValueError as e:
        raise ConfigError(f"'{name}' must be {type(ValueT).__name__}") from e


def _env_allowed_chats_ids(environ: Mapping[str, str]) -> list[int]:
    allowed_chats = environ.get("ARDTG_ALLOWED_CHATS")
    if allowed_chats is None:
        return []
    return [int(allowed_chats) for allowed_chats in allowed_chats.split(",")]


def _env_value_session_ttl(environ: Mapping[str, str]) -> float:
    ttl = _env_value("ARDTG_SESSION_LIFE_TIME", float, environ)
    return ttl if ttl is not None else DEFAULT_SESSION_TTL


def _optional_env(name: str, environ: Mapping[str, str]) -> str | None:
    return environ.get(name)


def _required_env(name: str, environ: Mapping[str, str]) -> str:
    value = environ.get(name)
    if value is None or value == "":
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


def _requred_url(name: str, environ: Mapping[str, str]) -> str:
    url = _required_env(name, environ)
    _validate_url(url)
    return url


def _requred_tg_token(name: str, environ: Mapping[str, str]) -> str:
    token = _required_env(name, environ)
    try:
        _ = validate_token(token)
    except ValueError as err:
        raise ConfigError from err
    return token


def _optional_url(name: str, environ: Mapping[str, str]) -> str | None:
    url = _optional_env(name, environ)
    if url is None:
        return None
    _validate_url(url)
    return url


@dataclass(frozen=True, slots=True)
class Config:
    telegram_token: str
    agent_url: str
    agent_datapath: str
    file_storage_path: str
    webhook_url: str | None
    sticker_pack: str | None
    notify_chat_id: int | None
    allowed_chats: list[int]
    session_life_time: float


def load_config(environ: Mapping[str, str]) -> Config:
    return Config(
        telegram_token=_requred_tg_token("ARDTG_TELEGRAM_TOKEN", environ),
        agent_url=_requred_url("ARDTG_AGENT_URL", environ),
        agent_datapath=_required_env("ARDTG_AGENT_DATAPATH", environ),
        file_storage_path=_required_env("ARDTG_FILESTORAGE_PATH", environ),
        webhook_url=_optional_url("ARDTG_WEBHOOK_URL", environ),
        sticker_pack=_optional_env("ARDTG_STICKER_PACK", environ),
        notify_chat_id=_env_value("ARDTG_NOTIFY_CHAT_ID", int, environ),
        allowed_chats=_env_allowed_chats_ids(environ),
        session_life_time=_env_value_session_ttl(environ),
    )
