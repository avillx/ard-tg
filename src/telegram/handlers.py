import logging

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
import arch_agent.models as models
import telegram.message_flusher as message_flusher
import telegram.tools as tools
from telegram import rich_message, sticker_cache
from telegram.typing_action import TypingAction

_TELEGRAM_GUIDE = """
# Gateway

You recieve user messages from messanger `Telegram`. markdown has fully support.
"""


class Service:
    _agent_service: agent.Service
    _session_service: agent.SessionService
    _sticker_cache: sticker_cache.StickerCache
    _file_storage: str
    _logger: logging.Logger

    def __init__(
        self,
        agent_service: agent.Service,
        session_service: agent.SessionService,
        sticker_cache: sticker_cache.StickerCache,
        sticker_pack: str,
        file_storage: str,
        logger: logging.Logger,
    ):
        self._logger = logger.getChild("Telegram.Hanlders")
        self._agent_service = agent_service
        self._sticker_cache = sticker_cache
        self._file_storage = file_storage
        self._sticker_pack = sticker_pack
        self._session_service = session_service

    def set_commands_prompt(self, bot: telebot.TeleBot):
        """
        Register allowed commands prompt for users in a bot
        """
        commands: list[telebot_types.BotCommand] = [
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
        """
        Register routes bot handlers
        """
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
        """
        Handler for process requests on consolidation.
        Expect call from `/consolidate` command
        """

        rich_msg = rich_message.RichMessage(
            chat_id=message.chat.id,
            bot=bot,
            draft_id=2,
        )

        rich_msg.append_text("💾 Consolidation started")

        def on_completion(completion: str) -> None:
            if completion is not None and completion != "":
                rich_msg.append_text(completion)

        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            try:
                self._agent_service.consolidate(on_completion)

            finally:
                rich_msg.send_finale()
                typing_action.stop_typing()

    def _handler_interruption(self, message: telebot_types.Message, bot: telebot.TeleBot):
        """
        Handler for interupt agent stream
        Expect call from `/interrupt` command
        """
        bot.send_message(message.chat.id, "🚧 Interrupting agent")
        self._agent_service.interrupt()

    def _handler_new_session(self, message: telebot_types.Message, bot: telebot.TeleBot):
        """
        Handler interrupt session and drop current session
        Expect call from `/new` command
        """
        self._agent_service.interrupt()
        self._session_service.drop()
        bot.send_message(message.chat.id, "💠 New session")

    def _handler_mcp(self, message: telebot_types.Message, bot: telebot.TeleBot):
        """
        Handler to fetch actual list of MCP
        Expect call from `/mcp` command
        Also allow mcp servers names as arguments e.g. `/mcp some-mcp-server some-other`
        """
        mcp_servers_list = self._agent_service.mcp_list()

        if len(mcp_servers_list) <= 0:
            bot.send_message(message.chat.id, "⚒️ Has no mcp servers")
            return

        response: list[str] = [fmt.mbold("⚒️ MCP servers:")]
        for name in mcp_servers_list:
            response.append(fmt.escape_markdown(f"- {name}"))

        response.append(fmt.mcite("For details: /tools <mcp_server>"))
        bot.send_message(message.chat.id, fmt.format_text(*response))

    def _handler_tasks(self, message: telebot_types.Message, bot: telebot.TeleBot):
        """
        Handler to fetch actual tasks config
        Expect call from `/tasks` command
        """
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
        """
        Handler fetch recent agent activity if it has
        Expect call from `/activity` command
        """
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
        """
        Handler fetch list of all tool servers
        Expect call from `/tools` command
        """
        tool_servers_list = self._agent_service.tool_list()

        response: list[str] = []
        response.append(fmt.mbold("🔧 Tool servers:"))
        for tool_server in tool_servers_list:
            response.append(fmt.escape_markdown(f"- {tool_server}"))

        repsonse_text = fmt.format_text(*response, separator="\n")
        bot.send_message(message.chat.id, repsonse_text)

    def _handler_general_message(self, message: telebot_types.Message, bot: telebot.TeleBot):
        """
        Handler to process all raw messages to agent
        """

        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            provided_tools = self._provided_tools(
                chat_id=message.chat.id,
                bot=bot,
            )

            rich_msg = rich_message.RichMessage(
                chat_id=message.chat.id,
                bot=bot,
                draft_id=1,
            )

            ev_handler = ChatEventHandler(
                rich_msg=rich_msg,
                bot=bot,
                typing=typing_action,
            )

            flusher = message_flusher.MessageFlusher(
                bot=bot,
                message=message,
                storage_path=self._file_storage,
            )

            # send request to agent
            try:
                self._agent_service.agent_request(
                    request=flusher.text(),
                    event_handler=ev_handler,
                    provided_tools=provided_tools,
                )

            except Exception as e:
                bot.send_message(message.chat.id, "⚠️ gateway problem")
                self._logger.error(f"gateway exception: {e}")
            finally:
                rich_msg.send_finale()

    # class helper
    def _provided_tools(
        self,
        chat_id: int,
        bot: telebot.TeleBot,
    ) -> list[agent.SafeTool]:

        provided_tools: list[agent.SafeTool] = [
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
            ),
        ]

        if self._sticker_pack != "":
            provided_tools.append(
                tools.SendStickerTool(
                    bot=bot,
                    chat_id=chat_id,
                    sticker_pack=self._sticker_cache.get_pack(self._sticker_pack),
                )
            )

        return provided_tools


class ChatEventHandler(agent.EventHandler):
    """
    Implementation of event handler to represent agent responses as
    telegram rich message
    """

    _bot: telebot.TeleBot
    _rich_message: rich_message.RichMessage
    _typing: TypingAction

    def __init__(
        self,
        rich_msg: rich_message.RichMessage,
        bot: telebot.TeleBot,
        typing: TypingAction,
    ) -> None:
        self._bot = bot
        self._typing = typing
        self._rich_message = rich_msg

    def process_completion(self, event: models.CompletionEvent):
        completion: str = event.completion

        if completion is None:
            completion = "\n"

        self._rich_message.append_text(completion)
        self._rich_message.append_tool_calls(event.tool_calls)
        self._rich_message.send_draft()

    def process_completion_mistake(self, event: models.CompletionMistakeEvent):
        warn = f"\n\n⚠️ agent make mistake: {fmt.escape_markdown(event.error)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    def process_compaction(self, event: models.CompactionEvent):
        self._rich_message.append_text("\n\n⚠️ session compacted")
        self._rich_message.send_draft()

    def process_tool_error(self, event: models.ToolErrorEvent):
        warn = f"\n\n⚠️ tool error: {fmt.escape_markdown(event.cause)}"
        self._rich_message.append_text(warn)
        self._rich_message.send_draft()

    def process_loop_exit(self, event: models.LoopExitEvent):
        if isinstance(event.cause, str) and event.cause != "":
            self._rich_message.append_text(f"\n\n⚠️ errors occured: {event.cause}")

        # send if is already done
        self._typing.stop_typing()
        self._rich_message.send_finale()

    def process_tool_result(self, event: models.ToolResultEvent):
        pass

    def process_error(self, err: models.Error):
        pass
