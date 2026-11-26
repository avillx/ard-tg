lazy import logging
from typing import override

lazy import telebot

from agent.chat import Tool,ToolArgs
from telegram.handler_general_message import TelegramToolFactory

class SendStickerTool(Tool):
    _bot: telebot.TeleBot
    _chat_id: int
    _sticker_pack: dict[str, str]

    def __init__(
        self,
        bot: telebot.TeleBot,
        chat_id: int,
        sticker_pack: dict[str, str],
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._sticker_pack = sticker_pack
        super().__init__(
            name="send_sticker",
            description="sends sticker in current chat",
            schema={
                "type": "object",
                "properties": {
                    "emoji": {
                        "type": "string",
                        "description": "sticker choosed by this emoji, only one emoji from enum",
                        "enum": list(self._sticker_pack.keys()),
                    }
                },
                "required": ["emoji"],
            },
        )

    @override
    def execute(self, args: ToolArgs) -> str:

        emoji = args.get("emoji")
        if not isinstance(emoji,str):
            return "'emoji' bad parameter type. expected string"

        file_id = self._sticker_pack.get(emoji)
        if file_id is None:
            return f"has no sticker for {emoji}"

        _ = self._bot.send_sticker(self._chat_id, file_id)
        return "sticker sended"


class StickerToolsFactory(TelegramToolFactory):
    _sticker_pack_name: str | None
    _sticker_packs: dict[str, dict[str, str]]
    _logger: logging.Logger

    def __init__(
        self,
        sticker_pack_name: str | None,
        logger: logging.Logger,
    ):
        self._sticker_packs = {}
        self._logger = logger.getChild("Telegram.StickerCache")
        self._sticker_pack_name = sticker_pack_name

    @override
    def get_tools(self,chat_id: int,bot: telebot.TeleBot) -> list[Tool]:
        pack = self._resolve_pack(bot)
        if pack is None:
            return []

        return [
            SendStickerTool(
                bot=bot,
                chat_id=chat_id,
                sticker_pack=pack,
            )
        ]

    def _resolve_pack(self,bot: telebot.TeleBot) -> dict[str, str] | None:

        # is is not setted just return None
        if self._sticker_pack_name is None:
            return None

        # try to find in cache
        sticker_pack = self._sticker_packs.get(self._sticker_pack_name)
        if sticker_pack is not None:
            return sticker_pack

        # download pack
        pack= self._download_pack(self._sticker_pack_name,bot)
        self._sticker_packs[self._sticker_pack_name] = pack
        return pack


    def _download_pack(self,sticker_pack_name:str,bot: telebot.TeleBot) -> dict[str, str]:

        self._logger.info("sticker pack %s: not found, getting from telegram", sticker_pack_name)
        sticker_set = bot.get_sticker_set(sticker_pack_name)
        new_sticker_pack: dict[str, str] = {}
        for s in sticker_set.stickers:
            if s.emoji is None:
                continue

            new_sticker_pack[s.emoji] = s.file_id

        return new_sticker_pack
