

from typing import override

import telebot

from ardtg.domain.notifications import MessangerBot


class TelegramMessangerBot(MessangerBot):
    _bot: telebot.TeleBot

    def __init__(self,bot: telebot.TeleBot) -> None:
        super().__init__()
        self._bot = bot

    @override
    def send(self, chat_id: int, message: str):
        _ = self._bot.send_message(chat_id=chat_id,text=message)
