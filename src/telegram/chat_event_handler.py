from typing import override

import telebot.formatting as fmt

from domain.chat import (
    CompactionEvent,
    CompletionEvent,
    CompletionMistakeEvent,
    ErrorEvent,
    EventHandler,
    LoopExitEvent,
    ProvidedToolCallEvent,
    Tool,
    ToolErrorEvent,
    ToolResultEvent,
)
from domain.tool import ToolExecutor
from telegram.rich_message import RichMessage
from telegram.typing_action import TypingAction


class TelegramEventHandler(EventHandler):
    """Event handler that renders agent responses as Telegram rich messages."""

    _rich_message: RichMessage
    _tool_executor: ToolExecutor
    _tools: list[Tool]
    _typing: TypingAction

    def __init__(
        self,
        rich_msg: RichMessage,
        tool_executor: ToolExecutor,
        tools: list[Tool],
        typing: TypingAction,
    ) -> None:
        super().__init__()
        self._tools = tools
        self._typing = typing
        self._rich_message = rich_msg
        self._tool_executor = tool_executor

    @override
    def process_completion(self, event: CompletionEvent):
        if event.completion != "":
            self._rich_message.append_text(event.completion)

        self._rich_message.append_tool_calls(event.tool_calls)
        self._rich_message.send_draft()

    @override
    def process_completion_mistake(self, event: CompletionMistakeEvent):
        warn = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(event.cause)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    @override
    def process_compaction(self, event: CompactionEvent):
        self._rich_message.append_text("\n\n⚠️ session compacted")
        self._rich_message.send_draft()

    @override
    def process_tool_error(self, event: ToolErrorEvent):
        warn = f"\n\n⚠️ tool error: {fmt.escape_markdown(event.cause)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    @override
    def process_loop_exit(self, event: LoopExitEvent):
        if isinstance(event.cause, str) and event.cause != "":
            self._rich_message.append_text(f"\n\n⚠️ errors occured: {event.cause}")

        # send if is already done
        self._typing.stop_typing()
        self._rich_message.send_final_message()

    @override
    def process_tool_result(self, event: ToolResultEvent):
        pass

    @override
    def process_provided_toolcall(self, event: ProvidedToolCallEvent):
        self._tool_executor.process_provided_toolcall(self._tools,event)

    @override
    def process_error(self, err: ErrorEvent):
        msg = f"\n\n⚠️ agent error: {fmt.escape_markdown(err.cause)}"
        self._rich_message.append_text(msg)
        self._rich_message.send_draft()
