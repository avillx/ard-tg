from typing import TYPE_CHECKING, override

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

from ardtg.telegram.service import CommandPrompter, MessageHandler

if TYPE_CHECKING:
    from ardtg.domain.task import TasksListService

_COMMAND = "tasks"


class TasksHandler(MessageHandler, CommandPrompter):
    """Handle fetch of the actual tasks config

    Expect call from `/tasks` command
    """

    _task_list_service: TasksListService

    def __init__(self, task_list_service: TasksListService):
        self._task_list_service = task_list_service

    @override
    def command_prompt(self) -> tuple[str, str]:
        return _COMMAND, "♻️ Show tasks"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        task_list = self._task_list_service.list()
        if len(task_list) <= 0:
            _ = bot.send_message(message.chat.id, "♻️ Agent return no tasks")
            return

        if len(task_list) <= 0:
            _ = bot.send_message(message.chat.id, "♻️ Has no tasks")
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
            _ = bot.send_message(message.chat.id, response)
