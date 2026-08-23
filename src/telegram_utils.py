import logging
import threading
from collections.abc import Callable

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import arch_agent.models as models


class StickerChache:
    _bot: telebot.TeleBot
    _sticker_packs : dict[dict[str,str]]
    _log : logging.Logger

    def __init__(self,bot: telebot.TeleBot, logger: logging.Logger):
        self._bot = bot
        self._sticker_packs = {}
        self._log = logger.getChild("Telegram.StickerChache")

    def get_pack(self,name:str) -> dict[str,str]:
        try:
            pack = self._sticker_packs[name]
            return pack
        except KeyError:
            self._log.info(f"sticker pack {name}: not found, getting from telegram")

            set = self._bot.get_sticker_set(name)
            if set is None:
                return None

            pack : dict[str,str] = {}
            for s in set.stickers:
                pack[s.emoji] = s.file_id

            self._sticker_packs[name] = pack

            return pack

class RichMessage:
    _bot : telebot.TeleBot
    _draft_id : int
    _chat_id : int
    _candidate : str
    _draft : str

    def __init__(
            self,
            bot : telebot.TeleBot,
            chat_id : int,
            draft_id : int
        ):
        self._bot = bot
        self._draft_id = draft_id
        self._chat_id = chat_id
        self._candidate = ""
        self._draft = ""

    def commit(self) -> None:
        if self._candidate == "":
            self._candidate = self._draft

        input = telebot_types.InputRichMessage(
            markdown= self._candidate
        )
        self._bot.send_rich_message(
            chat_id=self._chat_id,
            rich_message=input,
        )

    def append(self,text : str) -> None:
        self._draft += self._candidate
        self._candidate = text

        if self._draft == "":
            return

        # commit draft
        input = telebot_types.InputRichMessage(
            markdown= self._draft
        )
        self._bot.send_rich_message_draft(
            chat_id=self._chat_id,
            draft_id=self._draft_id,
            rich_message=input
        )

def tool_call_repr(call: models.ToolCall) -> str :

    if call is None:
        return ""

    if call.tool is None:
        return ""

    repr=f"{fmt.escape_markdown(call.tool)}"

    if call.args is None:
        return repr+"\n"

    repr += ":\n"
    args = call.args.to_dict()
    for k,v in args.items():
        arg_repr = ""
        if hasattr(v,"__repr__"):
            arg_repr : str = f"{k} = {v}"
        else:
            arg_repr : str = f"{k}"

        if len(arg_repr) > 40:
            arg_repr = f"{arg_repr[:40]}..."

        repr+=f"\n- {fmt.escape_markdown(arg_repr)}"

    return repr

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
                    # TODO: think about eliminating this shit
                    logging.error(f"typing fall with error: {e}")

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
