import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
from telegram.service import Handler


class McpHandler(Handler):
    """
    Handler to fetch actual list of MCP
    Expect call from `/mcp` command
    Also allow mcp servers names as arguments e.g. `/mcp some-mcp-server some-other`
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["mcp"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        mcp_servers_list = self._agent_service.mcp_list()

        if len(mcp_servers_list) <= 0:
            bot.send_message(message.chat.id, "⚒️ Has no mcp servers")
            return

        response: list[str] = [fmt.mbold("⚒️ MCP servers:")]
        for name in mcp_servers_list:
            response.append(fmt.escape_markdown(f"- {name}"))

        response.append(fmt.mcite("For details: /tools <mcp_server>"))
        bot.send_message(message.chat.id, fmt.format_text(*response))
