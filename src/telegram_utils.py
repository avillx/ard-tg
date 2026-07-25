import logging as log
import threading
from collections.abc import Callable

import telebot
import telebot.types as telebot_types
from telebot.handler_backends import BaseMiddleware, CancelUpdate

import tools


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
