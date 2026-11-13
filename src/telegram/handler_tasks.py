import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import agent
from telegram.service import Handler


class TasksHandler(Handler):
    """
    Handler to fetch actual tasks config
    Expect call from `/tasks` command
    """

    _agent_service: agent.Service

    def __init__(self, agent_service: agent.Service):
        self._agent_service = agent_service

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["tasks"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
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
