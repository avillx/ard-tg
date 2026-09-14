import logging

import telebot


class StickerCache:
    _bot: telebot.TeleBot
    _sticker_packs: dict[str, dict[str, str]]
    _log: logging.Logger

    def __init__(self, bot: telebot.TeleBot, logger: logging.Logger):
        self._bot = bot
        self._sticker_packs = {}
        self._log = logger.getChild("Telegram.StickerCache")

    def get_pack(self, name: str) -> dict[str, str]:
        """
        Return map of stickers
        - key emoji
        - value file_id

        Raise if stickerpack is not found in telegram
        """
        sticker_pack = self._sticker_packs.get(name)
        if sticker_pack is None:
            self._log.info(f"sticker pack {name}: not found, getting from telegram")

            set = self._bot.get_sticker_set(name)
            if set is None:
                raise Exception(f"sticker pack {name} is not found")

            new_sticker_pack: dict[str, str] = {}
            for s in set.stickers:
                if s.emoji is None:
                    continue

                new_sticker_pack[s.emoji] = s.file_id

            self._sticker_packs[name] = new_sticker_pack

            return new_sticker_pack

        return sticker_pack
