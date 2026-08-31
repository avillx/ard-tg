import logging

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
import arch_agent.models as models
import session
import telegram_utils as tg_utils
import tools


class Handlers:
    _agent_service: agent.AgentService
    _session_service: session.SessionService
    _sticker_chache: tg_utils.StickerChache
    _file_storage : str
    _logger: logging.Logger

    def __init__(
        self,
        agent_service: agent.AgentService,
        session_service: session.SessionService,
        sticker_chache: tg_utils.StickerChache,
        sticker_pack: str,
        file_storage : str,
        logger : logging.Logger,
    ):
        self._logger = logger.getChild("Telegram.Hanlders")
        self._agent_service = agent_service
        self._sticker_chache = sticker_chache
        self._file_storage = file_storage
        self._sticker_pack = sticker_pack
        self._session_service = session_service

    def set_commands_prompt(self,bot: telebot.TeleBot):
        commands : list[telebot_types.BotCommand] = [
            telebot_types.BotCommand("interrupt", "🚧 Interrupt agent response"),
            telebot_types.BotCommand("new", "💠 New session"),
            telebot_types.BotCommand("activity", "🗂 Show recent activity"),
            telebot_types.BotCommand("tasks", "♻️ Show tasks"),
            telebot_types.BotCommand("tools", "🔧 Show tools info"),
            telebot_types.BotCommand("mcp", "⚒️ Show list of MCP servers"),
            telebot_types.BotCommand("consolidate", "💾 Start memory consolidation process"),
        ]
        bot.set_my_commands(commands)

    def register_on(self, bot: telebot.TeleBot):

        bot.register_message_handler(
            self._handler_interruption, commands=["interrupt"], pass_bot=True
        )
        bot.register_message_handler(self._handler_tools, commands=["tools"], pass_bot=True)
        bot.register_message_handler(self._handler_tasks, commands=["tasks"], pass_bot=True)
        bot.register_message_handler(self._handler_mcp, commands=["mcp"], pass_bot=True)
        bot.register_message_handler(self._handler_activity, commands=["activity"], pass_bot=True)
        bot.register_message_handler(self._handler_new_session, commands=["new"], pass_bot=True)
        bot.register_message_handler(
            self._handler_consolidation,
                commands=["consolidate"],
                pass_bot=True,
        )
        bot.register_message_handler(
            self._handler_general_message,
            func=lambda message: True,
            pass_bot=True,
        )


    def _handler_consolidation(self, message: telebot_types.Message, bot: telebot.TeleBot):

        typing = tg_utils.TypingAction(
            chat_id=message.chat.id,
            bot=bot,
            logger=self._logger,
        )
        typing.start_typing()

        rich_message = tg_utils.RichMessage(
            chat_id = message.chat.id,
            bot = bot,
            draft_id = 2,
        )

        rich_message.append("💾 Consolidation started")

        def on_completion(completion: str) -> None:
            if completion is not None and completion != "":
                rich_message.append(completion)

        try:
            self._agent_service.consolidate(on_completion)
        finally:
            rich_message.commit()
            typing.stop_typing()

    def _handler_interruption(self, message: telebot_types.Message, bot: telebot.TeleBot):
        bot.send_message(message.chat.id, "🚧 Interrupting agent")
        self._agent_service.interrupt()

    def _handler_new_session(self, message: telebot_types.Message, bot: telebot.TeleBot):
        self._agent_service.interrupt()
        self._session_service.drop_session()
        bot.send_message(message.chat.id, "💠 New session")

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

            response.append("\nDetails: /tools <tool_server>")
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

        # save file via gateway

        rich_message = tg_utils.RichMessage(
            chat_id=message.chat.id,
            bot=bot,
            draft_id=1,
        )

        # on completion - sends draft in chat
        def on_completion(e: models.CompletionEvent) -> None:
            completion: str = e.completion

            if completion is None:
                completion = "\n"

            rich_message.append_text(completion)
            rich_message.append_tool_calls(e.tool_calls)
            rich_message.send_draft()


        # on completion mistake notify user about it
        def on_completion_mistake(e: models.CompletionMistakeEvent) -> None:
            warn = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(e.error)}"
            rich_message.append_text(warn)
            rich_message.send_draft()


        # on compactions sens notify message in chat
        def on_compaction(e: models.CompactionEvent) -> None:
            rich_message.append_text("\n\n⚠️ session compacted")
            rich_message.send_draft()


        # on tool error notify user about it
        def on_tool_error(e: models.ToolErrorEvent) -> None:
            warn = f"\n\n⚠️ tool error: {fmt.escape_markdown(e.cause)}"
            rich_message.append_text(warn)
            rich_message.send_draft()

        with tg_utils.TypingAction(bot,message.chat.id,self._logger) as typing:

            # on tool error notify user about it
            def on_loop_exit(e: models.LoopExitEvent) -> None:
                match e.cause: # avoid unset
                    case str():
                        if e.cause != "":
                            rich_message.append_text(f"\n\n⚠️ errors occured: {e.cause}")

                # send if is already done
                typing.stop_typing()
                rich_message.send_finale()

            # provided tools
            provided_tools = self._provided_tools(
                chat_id = message.chat.id,
                bot = bot,
            )

            flusher = tg_utils.MessageFlusher(
                bot=bot,
                message=message,
                storage_path=self._file_storage,
            )

            # send request to agent
            try:
                self._agent_service.agent_request(
                    request=flusher.text(),
                    on_completion=on_completion,
                    on_compaction=on_compaction,
                    on_compltion_mistake=on_completion_mistake,
                    on_loop_exit=on_loop_exit,
                    on_tool_error=on_tool_error,
                    provided_tools=provided_tools,
                )
            except Exception as e:
                bot.send_message(message.chat.id,"⚠️ gateway problem")
                self._logger.error(f"gateway exception: {e}")
            finally:
                rich_message.send_finale()


    # class helper
    def _provided_tools(
            self,
            chat_id:int,
            bot:telebot.TeleBot,
        ) -> list[tools.AgentTool]:

        provided_tools: list[tools.AgentTool] = [
            tools.SendPhotoTool(
                bot=bot,
                chat_id=chat_id,
            ),
            tools.SendFileTool(
                bot=bot,
                chat_id=chat_id,
            ),
            tools.SendVoiceTool(
                bot=bot,
                chat_id=chat_id,
            )
        ]

        if self._sticker_pack != "":
            provided_tools.append(
                tools.SendStickerTool(
                    bot=bot,
                    chat_id=chat_id,
                    sticker_pack=self._sticker_chache.get_pack(self._sticker_pack),
                )
            )

        return provided_tools


