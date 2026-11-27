from typing import TYPE_CHECKING, override

from ardtg.domain.attach import MessangerBot

if TYPE_CHECKING:
    import telebot


class TelegramMessangerBot(MessangerBot):
    _bot: telebot.TeleBot

    def __init__(self, bot: telebot.TeleBot) -> None:
        super().__init__()
        self._bot = bot

    @override
    def send(self, chat_id: int, message: str):
        _ = self._bot.send_message(chat_id=chat_id, text=message)
