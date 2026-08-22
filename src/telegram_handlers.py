import logging as log
from datetime import datetime

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
import arch_agent.models as models
import telegram_utils as tg_utils
import tools


class Handlers:
    _agent_service: agent.AgentService
    _sticker_chache: tg_utils.StickerChache

    def __init__(
        self,
        agent_service: agent.AgentService,
        sticker_chache: tg_utils.StickerChache,
        sticker_pack: str,
    ):
        self._agent_service = agent_service
        self._sticker_chache = sticker_chache
        self._sticker_pack = sticker_pack

    def register_on(self, bot: telebot.TeleBot):

        # set commands prompts
        bot.set_my_commands(
            [
                telebot_types.BotCommand("interrupt", "🚧 Interrupt agent response"),
                telebot_types.BotCommand("activity", "🗂 Show recent activity"),
                telebot_types.BotCommand("tasks", "♻️ Show tasks"),
                telebot_types.BotCommand("tools", "🔧 Show tools info"),
                telebot_types.BotCommand("mcp", "⚒️ Show list of MCP servers"),
                telebot_types.BotCommand("consolidate", "💾 Start memory consolidation process"),
            ]
        )

        # message handlers
        bot.register_message_handler(
            self._handler_interruption, commands=["interrupt"], pass_bot=True
        )
        bot.register_message_handler(self._handler_tools, commands=["tools"], pass_bot=True)
        bot.register_message_handler(self._handler_tasks, commands=["tasks"], pass_bot=True)
        bot.register_message_handler(self._handler_mcp, commands=["mcp"], pass_bot=True)
        bot.register_message_handler(self._handler_activity, commands=["activity"], pass_bot=True)
        bot.register_message_handler(
            tg_utils.with_typing(self._handler_consolidation),
            commands=["consolidate"],
            pass_bot=True,
        )
        bot.register_message_handler(
            tg_utils.with_typing(self._handler_general_message),
            func=lambda message: True,
            pass_bot=True,
        )

    def _handler_consolidation(self, message: telebot_types.Message, bot: telebot.TeleBot):

        _START_HEADER = "💾 Consolidation started"
        _FINALE_HEADER = "💾 Consolidation finished"

        bot.send_message(message.chat.id, _START_HEADER)

        last_completion = ""

        def on_completion(completion: str) -> None:
            nonlocal last_completion

            if completion is not None and completion != "":
                last_completion = completion
                input = telebot_types.InputRichMessage(markdown=completion)
                bot.send_rich_message_draft(message.chat.id, 1, input)

        self._agent_service.consolidate(on_completion)

        final = telebot_types.InputRichMessage(markdown=_FINALE_HEADER + "\n" + last_completion)
        bot.send_rich_message(message.chat.id, final)

    def _handler_interruption(self, message: telebot_types.Message, bot: telebot.TeleBot):
        bot.send_message(message.chat.id, "🚧 Interrupting agent")
        self._agent_service.interrupt()

    def _handler_mcp(self, message: telebot_types.Message, bot: telebot.TeleBot):
        mcp_servers_list = self._agent_service.mcp_list()

        if len(mcp_servers_list) <= 0:
            bot.send_message(message.chat.id, "⚒️ Has no mcp servers")
            return

        response: list[str] = [fmt.mbold("⚒️ MCP servers:")]
        for mcp_server in mcp_servers_list:
            response.append(fmt.escape_markdown(f"- {mcp_server.name} ({mcp_server.transport})"))
        response.append(fmt.mcite("For details: /tools <mcp_server>"))
        bot.send_message(message.chat.id, fmt.format_text(*response))

    def _handler_tasks(self, message: telebot_types.Message, bot: telebot.TeleBot):

        task_list = self._agent_service.task_list()
        if task_list is None:
            bot.send_message(message.chat.id, "♻️ Agent return no tasks")
            return

        if len(task_list) <= 0:
            bot.send_message(message.chat.id, "♻️ Has no tasks")
            return

        for task in task_list:
            response = fmt.format_text(
                fmt.mbold("♻️ Task: ") + fmt.escape_markdown(task.name),
                fmt.mbold("Schedule: ") + fmt.escape_markdown(task.schedule),
                fmt.mbold("State: ") + ("Enabled" if task.active else "Disabled"),
                fmt.mbold("Execution: ") + ("Once" if task.oneshot else "Regular"),
                fmt.mbold("Recipients: ")
                + fmt.escape_markdown(fmt.format_text(*task.recipients, ",")),
                fmt.mbold("Description: ") + fmt.escape_markdown(task.description),
            )
            bot.send_message(message.chat.id, response)

    def _handler_activity(self, message: telebot_types.Message, bot: telebot.TeleBot):
        today_activity = self._agent_service.today_activity()

        if len(today_activity) <= 0:
            bot.send_message(message.chat.id, "🗂 Agent has no activity for today")
            return

        for activity_record in today_activity:
            response: list[str] = []
            for line in activity_record.content.split("\n"):
                if line.find("##", 0, 2) != -1:
                    line = line.replace("##", "")
                    line = line.replace(" ", "")
                    line = fmt.mbold(line)
                    response.append(line)
                    continue

                response.append(fmt.escape_markdown(line))

            response = response[-30:]

            formatted = fmt.format_text(
                fmt.mbold(f"🗂 Recent activity for {activity_record.date}:"),
                *response,
            )

            bot.send_message(message.chat.id, formatted)

    def _handler_tools(self, message: telebot_types.Message, bot: telebot.TeleBot):
        tool_servers_list = self._agent_service.tool_list()

        args = message.text.split()[1:]

        # if has no requested servers then send list of all servers
        if len(args) <= 0:
            response: list[str] = []
            response.append(fmt.mbold("🔧 Tool servers:"))
            for tool_server in tool_servers_list:
                response.append(fmt.escape_markdown(f"- {tool_server.name}"))

            response.append(fmt.mcite("For current server: /tools <tool_server>"))
            repsonse_text = fmt.format_text(*response, separator="\n")
            bot.send_message(message.chat.id, repsonse_text)
            return

        # extract tool servers by name
        tool_servers: list[models.ToolServerInfo] = []
        for server_name in args:
            for t in tool_servers_list:
                if t.name == server_name:
                    tool_servers.append(t)

        if len(tool_servers) <= 0:
            bot.send_message(message.chat.id, f"unknown tool server {server_name}")
            return

        # send info on requested servers
        for tool_server in tool_servers:
            response = [fmt.mbold("🔧 " + fmt.escape_markdown(tool_server.name))]

            server_tools: list[models.ToolInfo] = tool_server.tools
            for tool_info in server_tools:
                response.append(
                    fmt.format_text(
                        fmt.mbold("Tool: " + fmt.escape_markdown(tool_info.name)),
                        fmt.escape_markdown(tool_info.description),
                    )
                )

            repsonse_text = fmt.format_text(*response, separator="\n\n")
            bot.send_message(message.chat.id, repsonse_text)

    def _handler_general_message(self, message: telebot_types.Message, bot: telebot.TeleBot):

        lastCompltionText = ""
        heap = ""

        # on tool error notify user about it
        def on_loop_exit(e: models.LoopExitEvent) -> None:
            nonlocal lastCompltionText

            match e.cause: # avoid unset
                case str():
                    if e.cause != "":
                        lastCompltionText += f"\n\n⚠️ errors occured: {e.cause}"

        # on completion - sends draft in chat
        def on_completion(e: models.CompletionEvent) -> None:
            nonlocal heap
            nonlocal lastCompltionText

            completion: str = e.completion
            if completion is None:
                return

            lastCompltionText=completion

            heap += f"\n{completion}"

            if e.tool_calls is not None:
                for call in e.tool_calls:
                    heap += f"\n{tool_call_repr(call)}\n"

            input = telebot_types.InputRichMessage(markdown=heap)
            bot.send_rich_message_draft(message.chat.id,1,input)

        # on completion mistake notify user about it
        def on_completion_mistake(e: models.CompletionMistakeEvent) -> None:
            nonlocal heap
            nonlocal lastCompltionText

            response = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(e.error)}"
            heap += f"\n{response}"
            lastCompltionText = response

            input = telebot_types.InputRichMessage(markdown=heap)
            bot.send_rich_message_draft(message.chat.id,1,input)

        # on compactions sens notify message in chat
        def on_compaction(e: models.CompactionEvent) -> None:
            nonlocal heap
            heap += "\n\n⚠️ session compacted"

            input = telebot_types.InputRichMessage(markdown=heap)
            bot.send_rich_message_draft(message.chat.id,1,input)

        # on tool error notify user about it
        def on_tool_error(e: models.ToolErrorEvent) -> None:
            nonlocal heap
            heap += f"\n\n⚠️ tool error: {fmt.escape_markdown(e.cause)}"

            input = telebot_types.InputRichMessage(markdown=heap)
            bot.send_rich_message_draft(message.chat.id,1,input)

        provided_tools: list[tools.AgentTool] = []
        if self._sticker_pack != "":
            sticker_tool = tg_utils.SendStickerTool(
                chat_id=message.chat.id,
                bot=bot,
                sticker_pack=self._sticker_chache.get_pack(self._sticker_pack),
            )
            provided_tools.append(sticker_tool)

        current_time = datetime.now().strftime("%y.%m.%d %H:%M")
        self._agent_service.agent_request(
            request=f"# From: {message.chat.first_name} ({current_time}):\n{message.text}",
            on_completion=on_completion,
            on_compaction=on_compaction,
            on_compltion_mistake=on_completion_mistake,
            on_loop_exit=on_loop_exit,
            on_tool_error=on_tool_error,
            provided_tools=provided_tools,
        )

        # send final message
        input = telebot_types.InputRichMessage(markdown=lastCompltionText)
        bot.send_rich_message(message.chat.id,input)


def tool_call_repr(call: models.ToolCall) -> str :

    repr=f"{fmt.escape_markdown(call.tool)}:"

    try:
        args = call.args.to_dict()
        for k,v in args.items():
            arg_repr = ""
            if hasattr(v,"__repr__"):
                arg_repr : str = f"{k}={v}"
            else:
                arg_repr : str = f"{k}"

            if len(arg_repr) > 40:
                arg_repr = f"{arg_repr[:40]}..."

            repr+=f"\n- {fmt.escape_markdown(arg_repr)}"

    except Exception as e:
        log.error(f"parse args for tool: {call.tool}: {e}")

    return repr
