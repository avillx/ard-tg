import telebot
import telebot.formatting as fmt

import agent
import ard.models as models
from telegram import rich_message
from telegram.typing_action import TypingAction


class ChatEventHandler(agent.EventHandler):
    """
    Implementation of event handler to represent agent responses as
    telegram rich message
    """

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

    def process_completion(self, event: models.CompletionEvent):
        completion: str = event.completion

        if completion is None:
            completion = "\n"

        self._rich_message.append_text(completion)
        self._rich_message.append_tool_calls(event.tool_calls)
        self._rich_message.send_draft()

    def process_completion_mistake(self, event: models.CompletionMistakeEvent):
        warn = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(event.error)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    def process_compaction(self, event: models.CompactionEvent):
        self._rich_message.append_text("\n\n⚠️ session compacted")
        self._rich_message.send_draft()

    def process_tool_error(self, event: models.ToolErrorEvent):
        warn = f"\n\n⚠️ tool error: {fmt.escape_markdown(event.cause)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    def process_loop_exit(self, event: models.LoopExitEvent):
        if isinstance(event.cause, str) and event.cause != "":
            self._rich_message.append_text(f"\n\n⚠️ errors occured: {event.cause}")

        # send if is already done
        self._typing.stop_typing()
        self._rich_message.send_finale()

    def process_tool_result(self, event: models.ToolResultEvent):
        pass

    def process_error(self, err: models.Error):
        pass
