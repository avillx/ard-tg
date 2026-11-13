import logging

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

lazy import ard.models as models


class RichMessage:
    _bot: telebot.TeleBot
    _draft_id: int
    _chat_id: int
    _candidate: str
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
        self._candidate = ""
        self._text_drafts = []
        self._is_finally_sended = False
        self._logger = logger

    def append_tool_calls(self, calls: list[models.ToolCall]) -> None:
        if not calls:
            return

        for call in calls:
            self._text_drafts.append(tool_call_repr(call))

    def append_text(self, text: str) -> None:
        if text == "":
            return

        self._candidate = text
        self._text_drafts.append(text)

    def send_draft(self):
        draft = "\n\n".join(self._text_drafts)

        rich_message = telebot_types.InputRichMessage(
            markdown=draft,
        )
        self._bot.send_rich_message_draft(
            chat_id=self._chat_id, draft_id=self._draft_id, rich_message=rich_message
        )

    def send_finale(self) -> None:
        if self._is_finally_sended:
            return

        if self._candidate == "":
            if len(self._text_drafts) <= 0:
                # nothing to send
                return

            self._candidate = self._text_drafts[-1]

        rich_message = telebot_types.InputRichMessage(markdown=self._candidate)

        try:
            self._bot.send_rich_message(
                chat_id=self._chat_id,
                rich_message=rich_message,
            )
        except Exception as e:  # noqa: BLE001 - rich messages are optional for the bot
            # A failed rich message falls back to plain text, which may fail as well and
            # must not break the update processing.
            self._logger.warning("cant send rich message, fallback is used: %s", e)
            self._bot.send_message(
                chat_id=self._chat_id,
                text=fmt.escape_markdown(self._candidate),
            )

        self._is_finally_sended = True


def tool_call_repr(call: models.ToolCall) -> str:

    if call is None:
        return ""

    if call.tool is None:
        return ""

    call_repr = f"{fmt.escape_markdown(call.tool)}"

    call_repr += ":\n"
    args = call.args.to_dict()

    for k, v in args.items():
        arg_repr = f"{k} = {v}" if hasattr(v, "__repr__") else f"{k}"
        if len(arg_repr) > 40:
            arg_repr = f"{arg_repr[:40]}..."

        call_repr += f"\n- {fmt.escape_markdown(arg_repr)}"

    return call_repr
