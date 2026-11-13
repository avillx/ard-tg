import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
from telegram.service import Handler


class ToolsHandler(Handler):
    """
    Handler fetch list of all tool servers
    Expect call from `/tools` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["tools"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        tool_servers_list = self._agent_service.tool_list()

        response: list[str] = []
        response.append(fmt.mbold("🔧 Tool servers:"))
        for tool_server in tool_servers_list:
            response.append(fmt.escape_markdown(f"- {tool_server}"))

        repsonse_text = fmt.format_text(*response, separator="\n")
        bot.send_message(message.chat.id, repsonse_text)
