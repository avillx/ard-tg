from typing import override

lazy import telebot
lazy import telebot.types as telebot_types

from telegram.service import CommandPrompter, MessageHandler
lazy import agent

_COMMAND = "interrupt"

class InterruptHandler(MessageHandler,CommandPrompter):
    """Handle interrupt of the agent stream

    Expect call from `/interrupt` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "🚧 Interrupt agent response"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        _ = bot.send_message(message.chat.id, "🚧 Interrupting agent")
        self._agent_service.interrupt()
