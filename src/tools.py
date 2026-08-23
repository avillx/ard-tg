from abc import ABC, abstractmethod

import telebot

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


class SendStickerTool(AgentTool):
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

    def name(self) -> str:
        return "send_sticker"

    def description(self) -> str:
        return "sends sticker in current chat"

    def schema(self) -> dict[str,any]:
        return {
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

    def execute(self,args : dict[str,any]) -> str:
        try:
            emoji = args["emoji"]
            file_id = self._sticker_pack[emoji]
            self._bot.send_sticker(self._chat_id,file_id)
            return "sticker sended"
        except KeyError:
            return f"has no sticker for {emoji}"
        except Exception:
            return "stricker tool occures errors"
