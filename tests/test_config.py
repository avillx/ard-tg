from collections.abc import Mapping

import pytest

from ardtg.build.config import ConfigError, load_config


@pytest.fixture
def vaild_env_config() -> Mapping[str,str]:
    return {
        "ARDTG_TELEGRAM_TOKEN":"sk-test-token",
        "ARDTG_AGENT_URL":"http://agent.my:8000",
        "ARDTG_AGENT_DATAPATH":"/any/path",
        "ARDTG_FILESTORAGE_PATH":"/any/path",
        "ARDTG_WEBHOOK_URL":"https://my.domain",
        "ARDTG_STICKER_PACK":"sticker_pack",
        "ARDTG_NOTIFY_CHAT_ID":"100",
        "ARDTG_ALLOWED_CHATS": "100,100,100",
        "ARDTG_SESSION_LIFE_TIME": "600",
    }

@pytest.fixture
def invaild_urls_env_config() -> Mapping[str,str]:
    return {
        "ARDTG_TELEGRAM_TOKEN":"sk-test-token",
        "ARDTG_AGENT_URL":"agent.my:8000",
        "ARDTG_AGENT_DATAPATH":"/any/path",
        "ARDTG_FILESTORAGE_PATH":"/any/path",
        "ARDTG_WEBHOOK_URL":"my.domain",
        "ARDTG_STICKER_PACK":"sticker_pack",
        "ARDTG_NOTIFY_CHAT_ID":"100",
        "ARDTG_ALLOWED_CHATS": "100,100,100",
        "ARDTG_SESSION_LIFE_TIME": "600",
    }

@pytest.fixture
def invaild_int_env_config() -> Mapping[str,str]:
    return {
        "ARDTG_TELEGRAM_TOKEN":"sk-test-token",
        "ARDTG_AGENT_URL":"http://agent.my:8000",
        "ARDTG_AGENT_DATAPATH":"/any/path",
        "ARDTG_FILESTORAGE_PATH":"/any/path",
        "ARDTG_WEBHOOK_URL":"https://my.domain",
        "ARDTG_STICKER_PACK":"sticker_pack",
        "ARDTG_NOTIFY_CHAT_ID":"xxx",
        "ARDTG_ALLOWED_CHATS": "100,xxx,100",
        "ARDTG_SESSION_LIFE_TIME": "600",
    }

@pytest.fixture
def invaild_with_no_required_env_config() -> Mapping[str,str]:
    return {
        "ARDTG_AGENT_DATAPATH":"/any/path",
        "ARDTG_FILESTORAGE_PATH":"/any/path",
        "ARDTG_WEBHOOK_URL":"https://my.domain",
    }

def test_config_happypath(vaild_env_config: Mapping[str,str]):
    _ = load_config(vaild_env_config)

def test_config_url_validation(invaild_urls_env_config: Mapping[str,str]):
    with pytest.raises(ConfigError):
        _ = load_config(invaild_urls_env_config)

def test_config_int_cast(invaild_int_env_config: Mapping[str,str]):
    with pytest.raises(ConfigError):
        _ = load_config(invaild_int_env_config)

def test_config_requirements_test(invaild_with_no_required_env_config: Mapping[str,str]):
    with pytest.raises(ConfigError):
        _ = load_config(invaild_with_no_required_env_config)
