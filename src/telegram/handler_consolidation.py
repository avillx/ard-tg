from typing import override
lazy import logging

lazy import telebot
lazy import telebot.types as telebot_types

from agent.chat import CompletionEvent, ErrorEvent
from agent.consolidation import ConsolidationEventHandler, Consolidator
from telegram.rich_message import RichMessage
from telegram.service import CommandPrompter, MessageHandler
from telegram.typing_action import TypingAction

CONSOLIDATION_DRAFT_ID = 2
_COMMAND = "consolidate"



class TelegramConsolidationEventHandler(ConsolidationEventHandler):
    _rich_message: RichMessage

    def __init__(self,rich_message: RichMessage) -> None:
        super().__init__()
        self._rich_message = rich_message

    @override
    def process_completion(self, event: CompletionEvent):
        if event.completion != "":
            self._rich_message.append_text(event.completion)
            self._rich_message.send_draft()

    @override
    def process_error(self, err: ErrorEvent):
        self._rich_message.append_text(f"⚠️ Consolidator error: {err.cause}")
        self._rich_message.send_draft()


class ConsolidationHandler(MessageHandler,CommandPrompter):
    """Handle requests for consolidation

    Expect call from `/consolidate` command
    """

    _consolidator: Consolidator
    _logger: logging.Logger

    def __init__(self, consolidator: Consolidator, logger: logging.Logger):
        self._consolidator = consolidator
        self._logger = logger.getChild("Telegram.ConsolidationHandler")

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "💾 Start memory consolidation process"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        rich_message = RichMessage(
            chat_id=message.chat.id,
            bot=bot,
            draft_id=CONSOLIDATION_DRAFT_ID,
            logger=self._logger,
        )
        rich_message.append_text("💾 Consolidation started")

        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            try:
                self._consolidator.consolidate(TelegramConsolidationEventHandler(
                    rich_message=rich_message
                ))

            finally:
                rich_message.send_final_message()
                typing_action.stop_typing()
