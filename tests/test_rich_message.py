import unittest.mock
from typing import Any, cast

import telebot.formatting as fmt

import arch_agent.models as models
from telegram.rich_message import RichMessage, tool_call_repr


def _tool_call(tool: str | None, args: dict[str, Any]) -> models.ToolCall:
    return models.ToolCall(id="i", tool=cast(str, tool), args=models.ToolCallArgs.from_dict(args))


def test_tool_call_repr_none() -> None:
    # signature says ToolCall, but tool_call_repr defensively handles None
    assert tool_call_repr(cast(models.ToolCall, cast(object, None))) == ""


def test_tool_call_repr_no_tool() -> None:
    assert tool_call_repr(_tool_call(None, {})) == ""


def test_tool_call_repr_basic() -> None:
    r = tool_call_repr(_tool_call("read", {"path": "/x"}))

    assert "read" in r
    # `=` is escaped by MarkdownV2
    assert fmt.escape_markdown("path = /x") in r


def test_tool_call_repr_truncates_long_value() -> None:
    long_value = "a" * 50
    r = tool_call_repr(_tool_call("read", {"path": long_value}))

    expected_arg = fmt.escape_markdown(("path = " + long_value)[:40] + "...")

    assert expected_arg in r
    assert long_value not in r


def test_tool_call_repr_empty_args() -> None:
    r = tool_call_repr(_tool_call("read", {}))

    assert r.startswith("read:\n")


def test_append_text_ignores_empty() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("")
    rm.send_finale()

    bot.send_rich_message.assert_not_called()
    bot.send_rich_message_draft.assert_not_called()


def test_send_draft() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=7)

    rm.append_text("hello")
    rm.send_draft()

    bot.send_rich_message_draft.assert_called_once()
    kwargs = bot.send_rich_message_draft.call_args.kwargs
    assert kwargs["chat_id"] == 1
    assert kwargs["draft_id"] == 7
    assert kwargs["rich_message"].markdown == "hello"


def test_send_draft_joins_multiple_texts() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.append_text("b")
    rm.send_draft()

    assert bot.send_rich_message_draft.call_args.kwargs["rich_message"].markdown == "a\n\nb"


def test_send_finale_uses_last_text_as_candidate() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.append_text("b")
    rm.send_finale()

    bot.send_rich_message.assert_called_once()
    assert bot.send_rich_message.call_args.kwargs["rich_message"].markdown == "b"


def test_send_finale_is_idempotent() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("a")
    rm.send_finale()
    rm.send_finale()

    assert bot.send_rich_message.call_count == 1


def test_send_finale_nothing_to_send() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.send_finale()

    bot.send_rich_message.assert_not_called()
    bot.send_message.assert_not_called()


def test_send_finale_tool_calls_only() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_tool_calls([_tool_call("read", {"path": "/x"})])
    rm.send_finale()

    bot.send_rich_message.assert_called_once()
    assert "read" in bot.send_rich_message.call_args.kwargs["rich_message"].markdown


def test_append_tool_calls_ignores_empty() -> None:
    bot = unittest.mock.Mock()
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_tool_calls([])
    # append_tool_calls defensively treats None as an empty list
    rm.append_tool_calls(cast(list[models.ToolCall], cast(object, None)))
    rm.send_finale()

    bot.send_rich_message.assert_not_called()


def test_send_finale_falls_back_to_plain_message_on_error() -> None:
    bot = unittest.mock.Mock()
    bot.send_rich_message.side_effect = Exception("boom")
    rm = RichMessage(bot=bot, chat_id=1, draft_id=1)

    rm.append_text("hi_there")
    rm.send_finale()

    bot.send_message.assert_called_once()
    kwargs = bot.send_message.call_args.kwargs
    assert kwargs["chat_id"] == 1
    assert kwargs["text"] == fmt.escape_markdown("hi_there")
