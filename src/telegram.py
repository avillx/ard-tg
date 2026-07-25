import logging as log
import threading
from collections.abc import Callable

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types
from telebot.handler_backends import BaseMiddleware, CancelUpdate

import api_bindings.arch_agent_api_client.models as models
import tools
from agent import AgentService


class UserWhitelistMiddleware(BaseMiddleware):
    _allowed_chats : list[int]

    def __init__(self, allowed_chats: list[int]):
        self.update_types = ["message", "chosen_inline_result", "chat_join_request"]
        self._allowed_chats = allowed_chats

    def pre_process(self, message, data):
        chat_id = self._extract_chat_id(message)
        if chat_id not in self._allowed_chats:
            log.info(f"update with unallowed chat id {chat_id} is blocked")
            return CancelUpdate()

    def post_process(self, message, data, exception):
        pass

    def _extract_chat_id(self, message) -> int:
        if hasattr(message, "chat"):
            return message.chat.id
        if hasattr(message, "from_user"):
            return message.from_user.id
        return 0

class StickerChache:
    _bot: telebot.TeleBot
    _sticker_packs : dict[dict[str,str]]

    def __init__(self,bot: telebot.TeleBot):
        self._bot = bot
        self._sticker_packs = {}

    def get_pack(self,name:str) -> dict[str,str]:
        try:
            pack = self._sticker_packs[name]
            return pack
        except KeyError:
            log.info(f"sticker pack {name}: not found, getting from telegram")

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
        except Exception:
            return "stricker tool occures errors"

class Handlers:
    agent_service : AgentService
    _sticker_chache : StickerChache

    def __init__(self, agent_service : AgentService, sticker_chache:StickerChache,sticker_pack:str):
        self.agent_service = agent_service
        self._sticker_chache = sticker_chache
        self._sticker_pack = sticker_pack

    def register_on(self,bot : telebot.TeleBot):

        # set commands prompts
        bot.set_my_commands(
            [
                telebot_types.BotCommand("ping","for ping test"),
                telebot_types.BotCommand("tools","show tools info")
            ]
        )

        # message handlers
        bot.register_message_handler(self._handler_ping,commands=['ping'],pass_bot=True)
        bot.register_message_handler(self._handler_tools,commands=['tools'],pass_bot=True)
        bot.register_message_handler(
            with_typing(self._handler_general_message),func=lambda message: True,pass_bot=True)

    def _handler_ping(self,message : telebot_types.Message,bot: telebot.TeleBot):
        bot.reply_to(message,"pong")

    def _handler_tools(self,message : telebot_types.Message,bot: telebot.TeleBot):
        tool_servers_list = self.agent_service.tool_list()

        args = message.text.split()[1:]

        # if has no requested servers then send list of all servers
        if len(args) <= 0:
            response : list[str] = []
            response.append(fmt.mbold("🔧 Tool servers:"))
            for tool_server in tool_servers_list:
                response.append(fmt.escape_markdown(f"- {tool_server.name}"))

            response.append(fmt.mcite("For current server: /tools <tool_server>"))
            repsonse_text = fmt.format_text(*response,separator="\n")
            bot.send_message(message.chat.id,repsonse_text)
            return

        # extract tool servers by name
        tool_servers : list[models.ToolServerInfo] = []
        for server_name in args:
            for t in tool_servers_list:
                if t.name == server_name:
                    tool_servers.append(t)

        if len(tool_servers) <= 0:
            bot.send_message(message.chat.id,f"unknown tool server {server_name}")
            return

        # send info on requested servers
        for tool_server in tool_servers:
            response = [fmt.mbold("🔧 "+fmt.escape_markdown(tool_server.name))]

            server_tools :list[models.ToolInfo] = tool_server.tools
            for tool_info in server_tools:
                response.append(fmt.format_text(
                        fmt.mbold("Tool: "+ fmt.escape_markdown(tool_info.name)) ,
                        fmt.escape_markdown(tool_info.description)
                    ))

            repsonse_text = fmt.format_text(*response,separator="\n\n")
            bot.send_message(message.chat.id,repsonse_text)


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
            message = f"somting goes wrong: {fmt.escape_markdown(e.payload.cause)}"
            bot.send_message(message.chat.id,message)

        provided_tools : list[tools.AgentTool] = []
        if self._sticker_pack != "" :
            sticker_tool = SendStickerTool(
                chat_id=message.chat.id,
                bot=bot,
                sticker_pack=self._sticker_chache.get_pack(self._sticker_pack)
            )
            provided_tools.append(sticker_tool)

        self.agent_service.agent_request(
            request=f"# {message.chat.first_name}:\n{message.text}",
            on_completion=on_completion,
            on_compaction=on_compaction,
            on_error=on_error,
            provided_tools = provided_tools
        )


def with_typing(
        handler : Callable[[telebot_types.Message,telebot.TeleBot],None]
) -> Callable[[telebot_types.Message,telebot.TeleBot],None]:

    def wrapped(message : telebot_types.Message,bot: telebot.TeleBot):
        stop_typing = threading.Event()

        def typing_loop():
            while not stop_typing.is_set():
                try:
                    bot.send_chat_action(chat_id=message.chat.id, action="typing")
                except Exception as e:
                    log.error(f"typing fall with error: {e}")

                stop_typing.wait(4)

        typing_thread = threading.Thread(target=typing_loop, daemon=True)
        typing_thread.start()

        try:
            handler(message,bot)
        finally:
            stop_typing.set()
            typing_thread.join()

    return wrapped

def run_bot_with_webhook(bot : telebot.TeleBot,url : str):
    import hmac
    import json
    import secrets
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    _SECRET_TOKEN = secrets.token_hex(32)
    _WEBHOOK_PATH = f"/bot/{secrets.token_hex(16)}"

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != _WEBHOOK_PATH:
                self.send_response(404)
                self.end_headers()
                return

            # virefy header token
            if not hmac.compare_digest(
                self.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
                _SECRET_TOKEN,
            ):
                self.send_response(403)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            try:
                update = telebot.types.Update.de_json(json.loads(body))
                bot.process_new_updates([update])
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    bot.remove_webhook()
    bot.set_webhook(
        url=url+_WEBHOOK_PATH,
        secret_token=_SECRET_TOKEN,
    )
    ThreadingHTTPServer(("0.0.0.0", 8443), Handler).serve_forever()
