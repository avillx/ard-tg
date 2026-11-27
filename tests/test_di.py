from ardtg.build.config import Config
from ardtg.build.di import build_app


def test_di_happypath():
    _ = build_app(Config(
        agent_datapath="",
        agent_url="",
        allowed_chats=[],
        file_storage_path="",
        notify_chat_id=0,
        session_life_time=0,
        sticker_pack=None,
        telegram_token="99999:sk-test-token",
        webhook_url=None,
    ))
