import logging
import threading

import telebot


class TypingAction:
    _typing_thread: threading.Thread
    _stop_typing_ev: threading.Event
    _is_typing: bool
    _bot: telebot.TeleBot
    _chat_id: int
    _logger: logging.Logger

    def __init__(
        self,
        bot: telebot.TeleBot,
        chat_id: int,
        logger: logging.Logger,
    ):

        self._bot = bot
        self._chat_id = chat_id
        self._stop_typing_ev = threading.Event()
        self._is_typing = False
        self._typing_thread = threading.Thread(
            target=self.typing_loop,
            daemon=True,
        )
        self._logger = logger.getChild("TypingAction")

    def typing_loop(self):
        while not self._stop_typing_ev.is_set():
            try:
                self._bot.send_chat_action(chat_id=self._chat_id, action="typing")
            except Exception as e:
                self._logger.error(f"typing fall with error: {e}")
            self._stop_typing_ev.wait(4)

    def start_typing(self):
        if not self._is_typing:
            self._typing_thread.start()
            self._is_typing = True

    def stop_typing(self):
        if self._is_typing:
            self._stop_typing_ev.set()
            self._typing_thread.join()
            self._is_typing = False

    def __enter__(self) -> "TypingAction":
        self.start_typing()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop_typing()
