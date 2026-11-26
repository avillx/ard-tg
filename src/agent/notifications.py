from abc import ABC, abstractmethod
from typing import override
lazy import logging

from agent.attach import MessangerBot


class Notifier(ABC):
    @abstractmethod
    def notify_about_up(self):
        pass

    @abstractmethod
    def notify_about_down(self):
        pass


class BotNotifier(Notifier):
    _messanger_bot: MessangerBot
    _notify_chat_id: int
    _logger: logging.Logger

    def __init__(
        self,
        messanger_bot: MessangerBot,
        notify_chat_id: int,
        logger: logging.Logger,
    ) -> None:
        super().__init__()
        self._messanger_bot = messanger_bot
        self._notify_chat_id = notify_chat_id
        self._logger = logger.getChild("Notifier")

    def _notify(self, text: str) -> None:
        """Send a notification message with the given text to the selected chat."""
        try:
            self._messanger_bot.send(self._notify_chat_id,text)
        except Exception as e:  # noqa: BLE001 - notification must never break the bot
            self._logger.error("Failed notify about bot up: %s", e)

    @override
    def notify_about_up(self) -> None:
        self._notify("🔹 Bot is ready")

    @override
    def notify_about_down(self) -> None:
        self._notify("🔻 Bot is shutdown")


class PlaceholderNotifier(Notifier):
    _logger: logging.Logger

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self._logger = logger

    @override
    def notify_about_up(self) -> None:
        self._logger.info("Server up: no where to notify")

    @override
    def notify_about_down(self) -> None:
        self._logger.info("Server down: no where to notify")
