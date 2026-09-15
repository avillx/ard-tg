import unittest.mock

import telebot.formatting as fmt

import arch_agent.models as models
from telegram.rich_message import RichMessage, tool_call_repr


def _tool_call(tool: str | None, args: dict) -> models.ToolCall:
    return models.ToolCall(id="i", tool=tool, args=models.ToolCallArgs.from_dict(args))


# ---------------------------------------------------------------------------
# tool_call_repr
# ---------------------------------------------------------------------------


def test_tool_call_repr_none():
    assert tool_call_repr(None) == ""


def test_tool_call_repr_no_tool():
    assert tool_call_repr(_tool_call(None, {})) == ""


def test_tool_call_repr_basic():
    r = tool_call_repr(_tool_call("read", {"path": "/x"}))

    assert "read" in r
    # `=` is escaped by MarkdownV2
    assert fmt.escape_markdown("path = /x") in r


def test_tool_call_repr_truncates_long_value():
    long_value = "a" * 50
    r = tool_call_repr(_tool_call("read", {"path": long_value}))

    expected_arg = fmt.escape_markdown(("path = " + long_value)[:40] + "...")

    assert expected_arg in r
    assert long_value not in r


def test_tool_call_repr_empty_args():
    r = tool_call_repr(_tool_call("read", {}))

    assert r.startswith("read:\n")


# ---------------------------------------------------------------------------
# RichMessage
# ---------------------------------------------------------------------------


def test_append_text_ignores_empty():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("")
    rm.send_finale()

    bot.send_rich_message.assert_not_called()
    bot.send_rich_message_draft.assert_not_called()


def test_send_draft():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=7)

    rm.append_text("hello")
    rm.send_draft()

    bot.send_rich_message_draft.assert_called_once()
    kwargs = bot.send_rich_message_draft.call_args.kwargs
    assert kwargs["chat_id"] == 1
    assert kwargs["draft_id"] == 7
    assert kwargs["rich_message"].markdown == "hello"


def test_send_draft_joins_multiple_texts():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.append_text("b")
    rm.send_draft()

    assert bot.send_rich_message_draft.call_args.kwargs["rich_message"].markdown == "a\n\nb"


def test_send_finale_uses_last_text_as_candidate():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.append_text("b")
    rm.send_finale()

    bot.send_rich_message.assert_called_once()
    assert bot.send_rich_message.call_args.kwargs["rich_message"].markdown == "b"


def test_send_finale_is_idempotent():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.send_finale()
    rm.send_finale()

    assert bot.send_rich_message.call_count == 1


def test_send_finale_nothing_to_send():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.send_finale()

    bot.send_rich_message.assert_not_called()
    bot.send_message.assert_not_called()


def test_send_finale_tool_calls_only():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_tool_calls([_tool_call("read", {"path": "/x"})])
    rm.send_finale()

    bot.send_rich_message.assert_called_once()
    assert "read" in bot.send_rich_message.call_args.kwargs["rich_message"].markdown


def test_append_tool_calls_ignores_empty():
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_tool_calls([])
    rm.append_tool_calls(None)
    rm.send_finale()

    bot.send_rich_message.assert_not_called()


def test_send_finale_falls_back_to_plain_message_on_error():
    bot = unittest.mock.Mock()
    bot.send_rich_message.side_effect = Exception("boom")
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("hi_there")
    rm.send_finale()

    bot.send_message.assert_called_once()
    kwargs = bot.send_message.call_args.kwargs
    assert kwargs["chat_id"] == 1
    assert kwargs["text"] == fmt.escape_markdown("hi_there")