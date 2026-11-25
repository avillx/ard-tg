from typing import override

import telebot
import telebot.formatting as fmt

import agent
lazy import ard.models as models
lazy import telegram.rich_message as rich_message
lazy from telegram.typing_action import TypingAction


class ChatEventHandler(agent.EventHandler):
    """Event handler that renders agent responses as Telegram rich messages."""

    _bot: telebot.TeleBot
    _rich_message: rich_message.RichMessage
    _typing: TypingAction

    def __init__(
        self,
        rich_msg: rich_message.RichMessage,
        bot: telebot.TeleBot,
        typing: TypingAction,
    ) -> None:
        self._bot = bot
        self._typing = typing
        self._rich_message = rich_msg

    @override
    def process_completion(self, event: models.CompletionEvent):
        if event.completion != "":
            self._rich_message.append_text(event.completion)

        self._rich_message.append_tool_calls(event.tool_calls)
        self._rich_message.send_draft()

    @override
    def process_completion_mistake(self, event: models.CompletionMistakeEvent):
        warn = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(event.error)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    @override
    def process_compaction(self, event: models.CompactionEvent):
        self._rich_message.append_text("\n\n⚠️ session compacted")
        self._rich_message.send_draft()

    @override
    def process_tool_error(self, event: models.ToolErrorEvent):
        warn = f"\n\n⚠️ tool error: {fmt.escape_markdown(event.cause)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    @override
    def process_loop_exit(self, event: models.LoopExitEvent):
        if isinstance(event.cause, str) and event.cause != "":
            self._rich_message.append_text(f"\n\n⚠️ errors occured: {event.cause}")

        # send if is already done
        self._typing.stop_typing()
        self._rich_message.send_final_message()

    @override
    def process_tool_result(self, event: models.ToolResultEvent):
        pass

    @override
    def process_error(self, err: models.Error):
        msg = "\n\n⚠️ agent error"

        err_text = err.message
        if isinstance(err_text, str):
            msg += f": {fmt.escape_markdown(err_text)}"

        self._rich_message.append_text(msg)
        self._rich_message.send_draft()
