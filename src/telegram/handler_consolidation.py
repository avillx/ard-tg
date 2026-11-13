import logging

import telebot
import telebot.types as telebot_types

import agent
from telegram import rich_message
from telegram.service import Handler
from telegram.typing_action import TypingAction


class ConsolidationHandler(Handler):
    """
    Handler for process requests on consolidation.
    Expect call from `/consolidate` command
    """

    _agent_service: agent.Service
    _logger: logging.Logger

    def __init__(self, agent_service: agent.Service, logger: logging.Logger):
        self._agent_service = agent_service
        self._logger = logger.getChild("Telegram.ConsolidationHandler")

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["consolidate"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        rich_msg = rich_message.RichMessage(
            chat_id=message.chat.id,
            bot=bot,
            draft_id=2,
        )

        rich_msg.append_text("💾 Consolidation started")

        def on_completion(completion: str) -> None:
            if completion is not None and completion != "":
                rich_msg.append_text(completion)

        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            try:
                self._agent_service.consolidate(on_completion)

            finally:
                rich_msg.send_finale()
                typing_action.stop_typing()
