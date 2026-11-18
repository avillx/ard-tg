from abc import ABC, abstractmethod

import telebot
import telebot.types as telebot_types

TELEGRAM_GUIDE = """
# Gateway

You recieve user messages from messanger `Telegram`. markdown has fully support.

all attachments sended by user stores in `tmp/*` of your default cwd
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


class Service:
    _handlers: list[BasicHandler]

    def __init__(self, handlers: list[BasicHandler]):
        self._handlers = handlers

    def set_commands_prompt(self, bot: telebot.TeleBot):
        """Register allowed commands prompt for users in a bot."""
        commands: list[telebot_types.BotCommand] = [
            telebot_types.BotCommand("interrupt", "🚧 Interrupt agent response"),
            telebot_types.BotCommand("new", "💠 New session"),
            telebot_types.BotCommand("activity", "🗂 Show recent activity"),
            telebot_types.BotCommand("tasks", "♻️ Show tasks"),
            telebot_types.BotCommand("profile", "👤 Show agent profiles"),
            telebot_types.BotCommand("mcp", "⚒️ Show list of MCP servers"),
            telebot_types.BotCommand("consolidate", "💾 Start memory consolidation process"),
        ]
        bot.set_my_commands(commands)

    def register_handlers(self, bot: telebot.TeleBot):
        """Register routes bot handlers."""
        for handler in self._handlers:
            handler.register_on(bot)
