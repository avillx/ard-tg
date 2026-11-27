from typing import TYPE_CHECKING

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

if TYPE_CHECKING:
    import logging

    from ardtg.domain.chat import ToolCall

_TOOL_ARG_REPRESENT_LENGHT = 50

class RichMessage:
    _bot: telebot.TeleBot
    _draft_id: int
    _chat_id: int
    _last_agent_text: str
    _text_drafts: list[str]
    _is_finally_sended: bool
    _logger: logging.Logger

    def __init__(
        self,
        bot: telebot.TeleBot,
        chat_id: int,
        draft_id: int,
        logger: logging.Logger,
    ):
        self._bot = bot
        self._draft_id = draft_id
        self._chat_id = chat_id
        self._last_agent_text = ""
        self._text_drafts = []
        self._is_finally_sended = False
        self._logger = logger

    def append_tool_calls(self, calls: list[ToolCall]) -> None:
        if not calls:
            return

        for call in calls:
            self._text_drafts.append(tool_call_repr(call))

    def append_text(self, text: str) -> None:
        if text == "":
            return

        self._last_agent_text = text
        self._text_drafts.append(text)

    def send_draft(self):
        draft = "\n\n".join(self._text_drafts)

        rich_message = telebot_types.InputRichMessage(
            markdown=draft,
        )
        _ = self._bot.send_rich_message_draft(
            chat_id=self._chat_id, draft_id=self._draft_id, rich_message=rich_message
        )

    def send_final_message(self) -> None:
        text = self._get_final_text()
        if text is None:
            return

        if self._is_finally_sended:
            return
        self._send_with_fallback(text)
        self._is_finally_sended = True

    def _get_final_text(self) -> str | None:
        if self._last_agent_text != "":
            return self._last_agent_text

        if len(self._text_drafts) > 0:
            return self._text_drafts[-1]

        return None

    def _send_with_fallback(self, text:str) -> None:
        try:
            self._send_rich_message(text)
        except Exception as e:  # noqa: BLE001 - rich messages are optional for the bot
            # A failed rich message falls back to plain text, which may fail as well and
            # must not break the update processing.
            self._logger.warning("cant send rich message, fallback is used: %s", e)
            self._send_message(text)

    def _send_message(self, text:str) -> None:
        _ = self._bot.send_message(
            chat_id=self._chat_id,
            text=fmt.escape_markdown(text),
        )

    def _send_rich_message(self, text:str) -> None:
        _ = self._bot.send_rich_message(
            chat_id=self._chat_id,
            rich_message=telebot_types.InputRichMessage(markdown=text),
        )


def tool_call_repr(call: ToolCall) -> str:
    call_repr = f"{fmt.escape_markdown(call.tool)}:\n"

    for k, v in call.args.items():  # pyright: ignore[reportAny] - ensure tool scheme is not possible
        arg_repr = f"{k} = {v}" if hasattr(v, "__repr__") else f"{k}" # pyright: ignore[reportAny]
        if len(arg_repr) > _TOOL_ARG_REPRESENT_LENGHT:
            arg_repr = f"{arg_repr[:_TOOL_ARG_REPRESENT_LENGHT]}..."

        call_repr += f"\n- {fmt.escape_markdown(arg_repr)}"

    return call_repr
