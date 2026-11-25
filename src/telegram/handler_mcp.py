from typing import override

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

from telegram.service import CommandPrompter, MessageHandler
lazy import agent

_COMMAND = "mcp"

class MCPHandler(MessageHandler,CommandPrompter):
    """Handle fetch of the actual MCP list.

    Expect call from `/mcp` command. Also allow mcp servers names as arguments,
    e.g. `/mcp some-mcp-server some-other`.
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "⚒️ Show list of MCP servers"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        mcp_servers_list = self._agent_service.mcp_list()

        if len(mcp_servers_list) <= 0:
            _ = bot.send_message(message.chat.id, "⚒️ Has no mcp servers")
            return

        response: list[str] = [fmt.mbold("⚒️ MCP servers:")]
        for name in mcp_servers_list:
            response.append(fmt.escape_markdown(f"- {name}"))

        response.append(fmt.mcite("For details: /tools <mcp_server>"))
        _ = bot.send_message(message.chat.id, fmt.format_text(*response))
