from typing import override
lazy import logging

lazy import telebot
lazy import telebot.types as telebot_types

import telegram.rich_message as rich_message
from telegram.service import CommandPrompter, MessageHandler
from telegram.typing_action import TypingAction
lazy import agent

CONSOLIDATION_DRAFT_ID = 2

class ConsolidationHandler(MessageHandler,CommandPrompter):
    """Handle requests for consolidation

    Expect call from `/consolidate` command
    """

    _agent_service: agent.Service
    _logger: logging.Logger

    def __init__(self, agent_service: agent.Service, logger: logging.Logger):
        self._agent_service = agent_service
        self._logger = logger.getChild("Telegram.ConsolidationHandler")

    @override
    def command_prompt(self) -> tuple[str,str]:
        return "consolidate", "💾 Start memory consolidation process"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["consolidate"], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        rich_msg = rich_message.RichMessage(
            chat_id=message.chat.id,
            bot=bot,
            draft_id=CONSOLIDATION_DRAFT_ID,
            logger=self._logger,
        )

        rich_msg.append_text("💾 Consolidation started")

        def on_completion(completion: str) -> None:
            if completion != "":
                rich_msg.append_text(completion)

        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            try:
                self._agent_service.consolidate(on_completion)

            finally:
                rich_msg.send_final_message()
                typing_action.stop_typing()
