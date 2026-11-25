lazy import logging

lazy import telebot

import agent
import telegram.tools as tools


class StickerService:
    _bot: telebot.TeleBot
    _sticker_pack_name: str | None
    _sticker_packs: dict[str, dict[str, str]]
    _log: logging.Logger

    def __init__(
        self,
        bot: telebot.TeleBot,
        sticker_pack_name: str | None,
        logger: logging.Logger,
    ):
        self._bot = bot
        self._sticker_packs = {}
        self._log = logger.getChild("Telegram.StickerCache")
        self._sticker_pack_name = sticker_pack_name

    def get_tools(self,chat_id: int) -> list[agent.Tool]:
        pack = self._resolve_pack()
        if pack is None:
            return []

        return [
            tools.SendStickerTool(
                bot=self._bot,
                chat_id=chat_id,
                sticker_pack=pack,
            )
        ]

    def _resolve_pack(self) -> dict[str, str] | None:

        # is is not setted just return None
        if self._sticker_pack_name is None:
            return None

        # try to find in chached
        sticker_pack = self._sticker_packs.get(self._sticker_pack_name)
        if sticker_pack is not None:
            return sticker_pack


        pack= self._download_pack(self._sticker_pack_name)
        self._sticker_packs[self._sticker_pack_name] = pack
        return pack


    def _download_pack(self,sticker_pack_name:str) -> dict[str, str]:

        self._log.info("sticker pack %s: not found, getting from telegram", sticker_pack_name)
        sticker_set = self._bot.get_sticker_set(sticker_pack_name)
        new_sticker_pack: dict[str, str] = {}
        for s in sticker_set.stickers:
            if s.emoji is None:
                continue

            new_sticker_pack[s.emoji] = s.file_id

        return new_sticker_pack
