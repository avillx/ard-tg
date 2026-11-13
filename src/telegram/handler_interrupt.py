lazy import telebot
lazy import telebot.types as telebot_types

from telegram.service import Handler
lazy import agent


class InterruptHandler(Handler):
    """Handle interrupt of the agent stream

    Expect call from `/interrupt` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["interrupt"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        bot.send_message(message.chat.id, "🚧 Interrupting agent")
        self._agent_service.interrupt()
