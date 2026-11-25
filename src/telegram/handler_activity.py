from typing import override

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

from telegram.service import CommandPrompter, MessageHandler
lazy import agent

_COMMAND = "activity"

class ActivityHandler(MessageHandler,CommandPrompter):
    """Handle fetch of recent agent activity, if any

    Expect call from `/activity` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "🗂 Show recent activity"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        today_activity = self._agent_service.today_activity()

        if len(today_activity) <= 0:
            _ = bot.send_message(message.chat.id, "🗂 Agent has no activity for today")
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

            _ = bot.send_message(message.chat.id, formatted)
