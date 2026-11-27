from typing import TYPE_CHECKING, override

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

from ardtg.telegram.service import CommandPrompter, MessageHandler

if TYPE_CHECKING:
    from ardtg.domain.mcp import MCPRepo

_COMMAND = "mcp"


class MCPHandler(MessageHandler, CommandPrompter):
    """Handle fetch of the actual MCP list.

    Expect call from `/mcp` command. Also allow mcp servers names as arguments,
    e.g. `/mcp some-mcp-server some-other`.
    """

    _mcp_repo: MCPRepo

    def __init__(self, mcp_repo: MCPRepo):
        self._mcp_repo = mcp_repo

    @override
    def command_prompt(self) -> tuple[str, str]:
        return _COMMAND, "⚒️ Show list of MCP servers"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        mcp_servers_list = self._mcp_repo.mcp_list()

        if len(mcp_servers_list) <= 0:
            _ = bot.send_message(message.chat.id, "⚒️ Has no mcp servers")
            return

        response: list[str] = [fmt.mbold("⚒️ MCP servers:")]
        for name in mcp_servers_list:
            response.append(fmt.escape_markdown(f"- {name}"))

        _ = bot.send_message(message.chat.id, fmt.format_text(*response))
