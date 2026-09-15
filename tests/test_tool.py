import unittest.mock

import pytest
from telebot import types as telebot_types

import agent.tool
import telegram.tools as tg_tools
from helpers import FakeTool, FailingTool


# ---------------------------------------------------------------------------
# SafeTool / create_provided_tool_server
# ---------------------------------------------------------------------------


def test_safe_tool_execute_passthrough():
    t = FakeTool(result="hello")

    assert t.execute({"a": 1}) == "hello"
    assert t.executed_args == {"a": 1}


def test_safe_tool_execute_wraps_exception():
    t = FailingTool()

    assert t.execute({}) == "error: kaboom"


def test_create_provided_tool_server():
    t = FakeTool(name="f", description="d", schema={"type": "object"})

    srv = agent.tool.create_provided_tool_server([t])

    assert len(srv.tools) == 1
    assert srv.tools[0].name == "f"
    assert srv.tools[0].description == "d"
    assert srv.tools[0].schema.to_dict() == {"type": "object"}


# ---------------------------------------------------------------------------
# SendPhotoTool / SendFileTool / SendVoiceTool
# ---------------------------------------------------------------------------

MEDIA_TOOLS = [
    (tg_tools.SendPhotoTool, "send_photo", "photo", "photo sended"),
    (tg_tools.SendFileTool, "send_document", "document", "file sended"),
    (tg_tools.SendVoiceTool, "send_voice", "voice", "voice sended"),
]


@pytest.mark.parametrize("tool_cls", [cls for cls, _, _, _ in MEDIA_TOOLS])
def test_send_media_missing_path_key(tool_cls):
    bot = unittest.mock.Mock()
    t = tool_cls(bot=bot, chat_id=1)

    # safe tool wrapper turns KeyError into "error: 'path'"
    assert t.execute({}) == "error: 'path'"
    bot.assert_not_called()


@pytest.mark.parametrize("tool_cls", [cls for cls, _, _, _ in MEDIA_TOOLS])
def test_send_media_none_path(tool_cls):
    bot = unittest.mock.Mock()
    t = tool_cls(bot=bot, chat_id=1)

    assert t.execute({"path": None}) == "path is required"
    bot.assert_not_called()


@pytest.mark.parametrize("tool_cls", [cls for cls, _, _, _ in MEDIA_TOOLS])
@pytest.mark.xfail(
    strict=True,
    reason="code bug: `if args['path'] is None or ''` never treats empty string as missing path",
)
def test_send_media_empty_path_bug(tool_cls):
    bot = unittest.mock.Mock()
    t = tool_cls(bot=bot, chat_id=1)

    assert t.execute({"path": ""}) == "path is required"
    bot.assert_not_called()


@pytest.mark.parametrize("tool_cls,send_method,payload_key,result_text", MEDIA_TOOLS)
def test_send_media_valid(tmp_path, tool_cls, send_method, payload_key, result_text):
    p = tmp_path / "file.bin"
    p.write_bytes(b"\x00\x01\x02")

    bot = unittest.mock.Mock()
    t = tool_cls(bot=bot, chat_id=42)

    assert t.execute({"path": str(p)}) == result_text

    send_call = getattr(bot, send_method)
    send_call.assert_called_once()
    kwargs = send_call.call_args.kwargs
    assert kwargs["chat_id"] == 42
    assert isinstance(kwargs[payload_key], telebot_types.InputFile)


# ---------------------------------------------------------------------------
# SendStickerTool
# ---------------------------------------------------------------------------


def _sticker_tool(bot=None, chat_id=1, pack=None):
    return tg_tools.SendStickerTool(
        bot=bot or unittest.mock.Mock(),
        chat_id=chat_id,
        sticker_pack=pack if pack is not None else {"😀": "file_id_1", "🐱": "file_id_2"},
    )


def test_send_sticker_missing_emoji():
    t = _sticker_tool()
    assert t.execute({}) == "'emoji' parameter is required"


def test_send_sticker_unknown_emoji():
    t = _sticker_tool()
    assert t.execute({"emoji": "🚀"}) == "has no sticker for 🚀"


def test_send_sticker_ok():
    bot = unittest.mock.Mock()
    t = _sticker_tool(bot=bot, chat_id=42)

    assert t.execute({"emoji": "😀"}) == "sticker sended"
    bot.send_sticker.assert_called_once_with(42, "file_id_1")


def test_send_sticker_schema_contains_enum():
    t = _sticker_tool()

    schema = t.schema()

    assert schema["type"] == "object"
    assert schema["properties"]["emoji"]["enum"] == ["😀", "🐱"]
    assert "emoji" in schema["required"]