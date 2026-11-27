from pathlib import Path
from typing import override

import telebot
from telebot import types as telebot_types

from ardtg.domain.chat import Tool, ToolArgs
from telegram.handler_general_message import TelegramToolFactory


class FSToolsFactory(TelegramToolFactory):
    @override
    def get_tools(self, chat_id: int, bot: telebot.TeleBot) -> list[Tool]:
        return [
            SendPhotoTool(
                bot=bot,
                chat_id=chat_id,
            ),
            SendFileTool(
                bot=bot,
                chat_id=chat_id,
            ),
            SendVoiceTool(
                bot=bot,
                chat_id=chat_id,
            ),
        ]


class SendPhotoTool(Tool):
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
    def execute(self, args: ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"

        with Path(p).open("rb") as f:
            _ = self._bot.send_photo(chat_id=self._chat_id, photo=telebot_types.InputFile(f))
        return "photo sended"


class SendFileTool(Tool):
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
    def execute(self, args: ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"
        with Path(p).open("rb") as f:
            _ = self._bot.send_document(chat_id=self._chat_id, document=telebot_types.InputFile(f))
        return "file sended"


class SendVoiceTool(Tool):
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
    def execute(self, args: ToolArgs) -> str:
        p = args.get("path")
        if not isinstance(p, str) or p == "":
            return "path is required"

        with Path(p).open("rb") as f:
            _ = self._bot.send_voice(chat_id=self._chat_id, voice=telebot_types.InputFile(f))
        return "voice sended"
