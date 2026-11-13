import telebot
import telebot.types as telebot_types

import agent
from telegram.service import Handler


class NewSessionHandler(Handler):
    """
    Handler interrupt session and drop current session
    Expect call from `/new` command
    """

    _agent_service: agent.Service
    _session_service: agent.SessionService

    def __init__(
        self,
        agent_service: agent.Service,
        session_service: agent.SessionService,
    ):
        self._agent_service = agent_service
        self._session_service = session_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["new"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        self._agent_service.interrupt()
        self._session_service.drop()
        bot.send_message(message.chat.id, "💠 New session")
