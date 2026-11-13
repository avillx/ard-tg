lazy import telebot
lazy import telebot.types as telebot_types

from telegram.service import Handler
lazy import agent


class NewSessionHandler(Handler):
    """Handle interrupt of the current session and drop it

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
