from abc import ABC, abstractmethod

import telebot
from telebot import types as telebot_types

import arch_agent.models as models


class AgentTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def schema(self) -> dict[str,any]:
        pass

    @abstractmethod
    def execute(self,ags : dict[str,any]) -> str:
        pass

def create_provided_tool_server(tools : list[AgentTool]) -> models.ProvidedToolServer:

    provided_tools : list[models.ProvidedTool] = []

    for t in tools:
        provided_tools.append(
            models.ProvidedTool(
                name=t.name(),
                description=t.description(),
                schema=models.ProvidedToolSchema.from_dict(t.schema()),
            )
        )

    return models.ProvidedToolServer(tools=provided_tools)


class SafeTool(AgentTool):
    _name:str
    _desctiption:str
    _schema:dict[str,any]

    def __init__(
            self,name:str,
            description:str,
            schema:dict[str,any],
        ):
        self._name=name
        self._desctiption=description
        self._schema=schema

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._desctiption

    def schema(self) -> dict[str,any]:
        return self._schema

    def execute(self,args : dict[str,any]) -> str:
        try:
            return self._execute(args)
        except Exception as e:
            return f"error: {e}"

    @abstractmethod
    def _execute(self,ags : dict[str,any]) -> str:
        pass

class SendStickerTool(SafeTool):
    _bot: telebot.TeleBot
    _chat_id: int
    _sticker_pack : dict[str,str]

    def __init__(
            self,
            bot: telebot.TeleBot,
            chat_id: int,
            sticker_pack : dict[str,str],
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
                        "type":        "string",
                        "description": "sticker choosed by this emoji, only one emoji from enum",
                        "enum" : list(self._sticker_pack.keys())
                    }
                },
                "required":["emoji"]
            }
        )

    def _execute(self,args : dict[str,any]) -> str:
        try:
            emoji = args["emoji"]
            file_id = self._sticker_pack[emoji]
            self._bot.send_sticker(self._chat_id,file_id)
            return "sticker sended"
        except KeyError:
            return f"has no sticker for {emoji}"

class SendPhotoTool(SafeTool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self,bot: telebot.TeleBot,chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_photo",
            description="sends photo in actial chat",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type":        "string",
                        "description": "absolute path to photo",
                    }
                },
                "required":["path"]
            }
        )

    def _execute(self,args : dict[str,any]) -> str:
        if args["path"] is None or "":
            return "path is required"

        with open(args["path"],'rb') as f:
            self._bot.send_photo(
                chat_id=self._chat_id,
                photo=telebot_types.InputFile(f)
            )
        return "photo sended"


class SendFileTool(SafeTool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self,bot: telebot.TeleBot,chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_document",
            description= "attach file to conversation as document",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type":        "string",
                        "description": "absolute path to file",
                    }
                },
                "required":["path"]
            }
        )

    def _execute(self,args : dict[str,any]) -> str:
        if args["path"] is None or "":
            return "path is required"

        with open(args["path"],'rb') as f:
            self._bot.send_document(
                chat_id=self._chat_id,
                document=telebot_types.InputFile(f)
            )
        return "file sended"

class SendVoiceTool(SafeTool):
    _bot: telebot.TeleBot
    _chat_id: int

    def __init__(self,bot: telebot.TeleBot,chat_id: int):
        self._bot = bot
        self._chat_id = chat_id
        super().__init__(
            name="send_voice",
            description= "attach file to conversation as voice message",
            schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type":        "string",
                        "description": "absolute path to .ogg, .mp3",
                    }
                },
                "required":["path"]
            }
        )

    def _execute(self,args : dict[str,any]) -> str:
        if args["path"] is None or "":
            return "path is required"


        with open(args["path"],'rb') as f:
            self._bot.send_voice(
                chat_id=self._chat_id,
                voice=telebot_types.InputFile(f)
            )
        return "voice sended"

