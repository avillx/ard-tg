import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types
import api_bindings.arch_agent_api_client.models as models
from agent import AgentService
import tools


class StickerChache():
    _bot: telebot.TeleBot
    _sticker_packs : dict[dict[str,str]]

    def __init__(self,bot: telebot.TeleBot):
        self._bot = bot
        self._sticker_packs = {}

    def get_pack(self,name:str) -> dict[str,str]:
        try:
            pack = self._sticker_packs[name]
            return pack
        except:      
            set = self._bot.get_sticker_set(name)
            if set is None:
                return None

            pack : dict[str,str] = {}
            for s in set.stickers:
                pack[s.emoji] = s.file_id

            self._sticker_packs[name] = pack

            return pack


class SendStickerTool(tools.AgentTool):
    _bot: telebot.TeleBot
    _chat_id: int
    _sticker_pack : dict[str,str]

    def __init__(self,bot: telebot.TeleBot, chat_id: int, sticker_pack : dict[str,str]):
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
        except Exception as e:
            return "stricker tool occures errors"

class Handlers():
    agent_service : AgentService
    _sticker_chache : StickerChache

    def __init__(self, agent_service : AgentService, sticker_chache:StickerChache):
        self.agent_service = agent_service
        self._sticker_chache = sticker_chache

    def register_on(self,bot : telebot.TeleBot):
        bot.register_message_handler(self._handler_ping,commands=['ping'],pass_bot=True)
        bot.register_message_handler(self._handler_tools,commands=['tools'],pass_bot=True)
        bot.register_message_handler(self._handler_general_message,func=lambda message: True,pass_bot=True)

    def _handler_ping(self,message : telebot_types.Message,bot: telebot.TeleBot):
        bot.reply_to(message,"pong")

    def _handler_tools(self,message : telebot_types.Message,bot: telebot.TeleBot):
        tool_servers_list = self.agent_service.tool_list()

        for tool_server in tool_servers_list: 
            servers_list = [fmt.mbold("🔧 "+fmt.escape_markdown(tool_server.name))] 

            server_tools :list[models.ToolInfo] = tool_server.tools
            if server_tools is None:
                continue

            for tool_info in server_tools:
                servers_list.append(fmt.format_text(
                        fmt.mbold("Tool: "+ fmt.escape_markdown(tool_info.name)) ,
                        fmt.escape_markdown(tool_info.description)
                    ))
            
            repsonse = fmt.format_text(*servers_list,separator="\n\n")
            bot.send_message(message.chat.id,repsonse)


    def _handler_general_message(self,message : telebot_types.Message,bot: telebot.TeleBot):

        # on completion - sends result in chat
        def on_completion(c : models.ChatCompletionEvent) -> None:
            completion : str  = c.payload.completion
            if completion is None:
                return
                        
            for m in completion.split(sep="\n\n"):
                if m != "":
                    bot.send_message(message.chat.id,fmt.escape_markdown(m))

        # on compactions sens notify message in chat
        def on_compaction(c : models.ChatCompletionEvent) -> None:
            bot.send_message(message.chat.id,"⚠️ session compacted")

        # on error notify user about it
        def on_error(e : models.ChatErrorEvent) -> None:
            bot.send_message(message.chat.id,"somting goes wrong: " + fmt.escape_markdown(e.payload.cause))

 
        sticker_tool = SendStickerTool(
            chat_id=message.chat.id,
            bot=bot,
            sticker_pack=self._sticker_chache.get_pack("x44lab_alpha")
        )

        self.agent_service.agent_request(
            request=f"# {message.chat.first_name}:\n{message.text}",        
            on_completion=on_completion,
            on_compaction=on_compaction,
            on_error=on_error,
            provided_tools = [sticker_tool]
        )