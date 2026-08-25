import logging
import threading

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
    _text_drafts : list[str]
    _tool_calls_repr : str
    _is_finally_sended : bool

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
        self._text_drafts = []
        self._is_finally_sended = False

    def append_tool_calls(self, calls : list[models.ToolCall]) -> None:
        if not calls:
            return

        for call in calls:
            self._text_drafts.append(tool_call_repr(call))

    def append_text(self,text : str) -> None:
        if text == "":
            return

        self._candidate = text
        self._text_drafts.append(text)

    def send_draft(self):

        draft = "".join(self._text_drafts)

        input = telebot_types.InputRichMessage(
            markdown=draft,
        )
        self._bot.send_rich_message_draft(
            chat_id=self._chat_id,
            draft_id=self._draft_id,
            rich_message=input
        )

    def send_finale(self) -> None:
        if self._is_finally_sended:
            return

        if self._candidate == "":
            if len(self._text_drafts) <= 0:
                raise(Exception("attempt to send empty rich message"))

            self._candidate = self._text_drafts[-1]

        input = telebot_types.InputRichMessage(
            markdown= self._candidate
        )

        try:
            self._bot.send_rich_message(
                chat_id=self._chat_id,
                rich_message=input,
            )
        except Exception as e:
            self._bot.send_message(fmt.escape_markdown(self._candidate))
            print(f"{e}")


        self._is_finally_sended = True

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

class TypingAction:
    _typing_thread : threading.Thread
    _stop_typing_ev : threading.Event
    _is_typing : bool
    _bot : telebot.TeleBot
    _chat_id : int
    _logger:logging.Logger

    def __init__(
            self,
            bot: telebot.TeleBot,
            chat_id:int,
            logger:logging.Logger,
        ):

        self._bot = bot
        self.chat_id = chat_id
        self._stop_typing_ev = threading.Event()
        self._is_typing = False
        self._typing_thread = threading.Thread(
            target=self.typing_loop,
            daemon=True,
        )
        self._logger = logger.getChild("TypingAction")

    def typing_loop(self):
        while not self._stop_typing_ev.is_set():
            try:
                self._bot.send_chat_action(chat_id=self._chat_id, action="typing")
            except Exception as e:
                self._logger.error(f"typing fall with error: {e}")
            self._stop_typing_ev.wait(4)

    def start_typing(self):
        if not self.is_typing:
            self._typing_thread.start()
            self.is_typing = True

    def stop_typing(self):
        if self.is_typing:
            self.stop_typing_ev.set()
            self.typing_thread.join()
            self.is_typing = False

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
