import logging
from abc import ABC, abstractmethod
from cmath import log

import telebot


class Notifier(ABC):
    @abstractmethod
    def notify_about_up(self):
        pass

    @abstractmethod
    def notify_about_down(self):
        pass


class TelegramNotifier(Notifier):
    _bot: telebot.TeleBot
    _notify_chat_id: int
    _logger: logging.Logger

    def __init__(self, bot: telebot.TeleBot, notify_chat_id: int, logger: logging.Logger) -> None:
        super().__init__()
        self._bot = bot
        self._notify_chat_id = notify_chat_id
        self._logger = logger

    def _notify(self, text: str) -> None:
        """
        Send notify message to selected chat with text
        """
        if self._notify_chat_id is None:
            return
        try:
            self._bot.send_message(
                chat_id=self._notify_chat_id,
                text=text,
            )
        except Exception as e:
            self._logger.error(f"Failed notify about bot up: {e}")

    def notify_about_up(self) -> None:
        """
        Send notify message to selected chat about bot has been connected to telegram
        """
        self._notify("🔹 Bot is ready")

    def notify_about_down(self) -> None:
        """
        Send notify message to selected chat about bot has been disconnected from telegram
        """
        self._notify("🔻 Bot is shutdown")


class PlaceholderNotifier(Notifier):
    _logger: logging.Logger

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()

    def notify_about_up(self) -> None:
        self._logger.info("Server up: no where to notify")

    def notify_about_down(self) -> None:
        self._logger.info("Server down: no where to notify")
