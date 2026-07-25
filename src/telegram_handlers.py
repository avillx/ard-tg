
import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
import api_bindings.arch_agent_api_client.models as models
import telegram_utils as tg_utils
import tools


class Handlers:
    _agent_service : agent.AgentService
    _sticker_chache : tg_utils.StickerChache

    def __init__(
            self,
            agent_service : agent.AgentService,
            sticker_chache:tg_utils.StickerChache,
            sticker_pack:str,
        ):
        self._agent_service = agent_service
        self._sticker_chache = sticker_chache
        self._sticker_pack = sticker_pack

    def register_on(self,bot : telebot.TeleBot):

        # set commands prompts
        bot.set_my_commands(
            [
                telebot_types.BotCommand("ping","for ping test"),
                telebot_types.BotCommand("tools","show tools info")
            ]
        )

        # message handlers
        bot.register_message_handler(self._handler_ping,commands=['ping'],pass_bot=True)
        bot.register_message_handler(self._handler_tools,commands=['tools'],pass_bot=True)
        bot.register_message_handler(
            tg_utils.with_typing(self._handler_general_message),
            func=lambda message: True,pass_bot=True)

    def _handler_ping(self,message : telebot_types.Message,bot: telebot.TeleBot):
        bot.reply_to(message,"pong")

    def _handler_tools(self,message : telebot_types.Message,bot: telebot.TeleBot):
        tool_servers_list = self._agent_service.tool_list()

        args = message.text.split()[1:]

        # if has no requested servers then send list of all servers
        if len(args) <= 0:
            response : list[str] = []
            response.append(fmt.mbold("🔧 Tool servers:"))
            for tool_server in tool_servers_list:
                response.append(fmt.escape_markdown(f"- {tool_server.name}"))

            response.append(fmt.mcite("For current server: /tools <tool_server>"))
            repsonse_text = fmt.format_text(*response,separator="\n")
            bot.send_message(message.chat.id,repsonse_text)
            return

        # extract tool servers by name
        tool_servers : list[models.ToolServerInfo] = []
        for server_name in args:
            for t in tool_servers_list:
                if t.name == server_name:
                    tool_servers.append(t)

        if len(tool_servers) <= 0:
            bot.send_message(message.chat.id,f"unknown tool server {server_name}")
            return

        # send info on requested servers
        for tool_server in tool_servers:
            response = [fmt.mbold("🔧 "+fmt.escape_markdown(tool_server.name))]

            server_tools :list[models.ToolInfo] = tool_server.tools
            for tool_info in server_tools:
                response.append(fmt.format_text(
                        fmt.mbold("Tool: "+ fmt.escape_markdown(tool_info.name)) ,
                        fmt.escape_markdown(tool_info.description)
                    ))

            repsonse_text = fmt.format_text(*response,separator="\n\n")
            bot.send_message(message.chat.id,repsonse_text)


    def _handler_general_message(self,message : telebot_types.Message,bot: telebot.TeleBot):

        # on completion - sends result in chat
        def on_completion(c : models.ChatCompletionEvent) -> None:
            completion : str  = c.payload.completion
            if completion is None:
                return

            for m in completion.split(sep="\n\n"):
                if m != "":
                    bot.send_message(message.chat.id,fmt.escape_markdown(m))

        # on compactions sens notify message in chat
        def on_compaction(c : models.ChatCompletionEvent) -> None:
            bot.send_message(message.chat.id,"⚠️ session compacted")

        # on error notify user about it
        def on_error(e : models.ChatErrorEvent) -> None:
            message = f"somting goes wrong: {fmt.escape_markdown(e.payload.cause)}"
            bot.send_message(message.chat.id,message)

        provided_tools : list[tools.AgentTool] = []
        if self._sticker_pack != "" :
            sticker_tool = tg_utils.SendStickerTool(
                chat_id=message.chat.id,
                bot=bot,
                sticker_pack=self._sticker_chache.get_pack(self._sticker_pack)
            )
            provided_tools.append(sticker_tool)

        self._agent_service.agent_request(
            request=f"# {message.chat.first_name}:\n{message.text}",
            on_completion=on_completion,
            on_compaction=on_compaction,
            on_error=on_error,
            provided_tools = provided_tools
        )
