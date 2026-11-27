from abc import ABC, abstractmethod

import telebot
import telebot.types as telebot_types

TELEGRAM_GUIDE = """
## Gateway

You recieve user messages from messanger `Telegram`. markdown has fully support.
- All attachments sended by user stores in `tmp/*` of your default cwd
- To sent anything back it must also in `tmp` copy to `tmp` and then send it
"""


class BasicHandler(ABC):
    """Telegram route handler.

    Owns its update route and knows how to register it on a bot. Dependencies are
    passed in a constructor.
    """

    @abstractmethod
    def register_on(self, bot: telebot.TeleBot) -> None:
        pass


class MessageHandler(BasicHandler, ABC):
    @abstractmethod
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        pass


class CallBackQueryHandler(BasicHandler, ABC):
    @abstractmethod
    def handle(self, call: telebot_types.CallbackQuery, bot: telebot.TeleBot) -> None:
        pass


class CommandPrompter(ABC):
    @abstractmethod
    def command_prompt(self) -> tuple[str, str]:
        pass


class Service:
    _handlers: list[BasicHandler]
    _bot: telebot.TeleBot

    def __init__(
        self,
        handlers: list[BasicHandler],
        bot: telebot.TeleBot,
    ):
        self._handlers = handlers
        self._bot = bot

    def run(self):
        """Register routes bot handlers."""
        self.register_command_prompt()
        self.register_handlers()

    def register_command_prompt(self):
        """Register routes bot handlers."""

        command_prompts: list[telebot_types.BotCommand] = []

        for handler in self._handlers:
            if not isinstance(handler, CommandPrompter):
                continue
            command, description = handler.command_prompt()
            command_prompts.append(
                telebot_types.BotCommand(command, description),
            )

        _ = self._bot.set_my_commands(command_prompts)

    def register_handlers(self):
        """Register routes bot handlers."""
        for handler in self._handlers:
            handler.register_on(self._bot)
