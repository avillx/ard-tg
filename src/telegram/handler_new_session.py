from typing import override

lazy import telebot
lazy import telebot.types as telebot_types

from telegram.service import CommandPrompter, MessageHandler
lazy import agent

_COMMAND = "new"

class NewSessionHandler(MessageHandler,CommandPrompter):
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

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "💠 New session"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        self._agent_service.interrupt()
        self._session_service.drop()
        _ = bot.send_message(message.chat.id, "💠 New session")
