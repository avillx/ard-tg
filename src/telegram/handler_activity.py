import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

from telegram.service import Handler
lazy import agent


class ActivityHandler(Handler):
    """Handle fetch of recent agent activity, if any

    Expect call from `/activity` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["activity"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
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
