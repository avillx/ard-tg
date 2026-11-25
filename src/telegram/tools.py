from pathlib import Path
from typing import override

import telebot
from telebot import types as telebot_types

import agent


class SendStickerTool(agent.Tool):
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
    def execute(self, args: agent.ToolArgs) -> str:

        emoji = args.get("emoji")
        if not isinstance(emoji,str):
            return "'emoji' bad parameter type. expected string"

        file_id = self._sticker_pack.get(emoji)
        if file_id is None:
            return f"has no sticker for {emoji}"

        _ = self._bot.send_sticker(self._chat_id, file_id)
        return "sticker sended"


class SendPhotoTool(agent.Tool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self, bot: telebot.TeleBot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_photo",
            description="sends photo in actial chat",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "absolute path to photo",
                    }
                },
                "required": ["path"],
            },
        )

    @override
    def execute(self, args: agent.ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"

        with Path(p).open("rb") as f:
            _ = self._bot.send_photo(chat_id=self._chat_id, photo=telebot_types.InputFile(f))
        return "photo sended"


class SendFileTool(agent.Tool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self, bot: telebot.TeleBot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_document",
            description="attach file to conversation as document",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "absolute path to file",
                    }
                },
                "required": ["path"],
            },
        )

    @override
    def execute(self, args: agent.ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"
        with Path(p).open("rb") as f:
            _ = self._bot.send_document(chat_id=self._chat_id, document=telebot_types.InputFile(f))
        return "file sended"


class SendVoiceTool(agent.Tool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self, bot: telebot.TeleBot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_voice",
            description="attach file to conversation as voice message",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "absolute path to .ogg, .mp3",
                    }
                },
                "required": ["path"],
            },
        )

    @override
    def execute(self, args: agent.ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"

        with Path(p).open("rb") as f:
            _ = self._bot.send_voice(chat_id=self._chat_id, voice=telebot_types.InputFile(f))
        return "voice sended"
