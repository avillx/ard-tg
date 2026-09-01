import logging
import threading
from datetime import datetime
from pathlib import Path

import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types

import arch_agent.models as models

_TELEGRAM_GUIDE="""
# Gateway

You recieve user messages from messanger `Telegram`. markdown has fully support.
"""

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

class MessageFlusher:
    _text_repr : str
    _image_data : str
    _bot : telebot.TeleBot
    _storage_path : str

    def __init__(
            self, bot : telebot.TeleBot,
            message : telebot_types.Message,
            storage_path: str,
        ):
        self._storage_path = storage_path
        self._bot = bot

        # user message for agent
        current_time = datetime.now().strftime("%y.%m.%d %H:%M")
        self._text_repr = f"# From {message.chat.first_name} ({current_time}):"

        if message.photo is not None:
            p = message.photo[-1]
            path = self._save_file(
                p,
            )
            self._text_repr += f"\nPhoto saved on path: {path}"

        if message.audio is not None:
            path = self._save_file(
                message.audio,
            )
            self._text_repr += f"\nAudio saved on path: {path}"

        if message.video is not None:
            path = self._save_file(
                message.video,
            )
            self._text_repr += f"\nVideo saved on path: {path}"

        if message.video_note is not None:
            path = self._save_file(
                message.video_note,
            )
            self._text_repr += f"\nVideo note saved on path: {path}"

        if message.document is not None:
            path = self._save_file(
                message.document,
            )
            self._text_repr += f"\nDocument saved on path: {path}"

        if message.voice is not None:
            path = self._save_file(
                message.voice,
            )
            self._text_repr += f"\nVoice message saved on path: {path}"

        if message.sticker is not None:
            self._text_repr += f"\nSticker: {message.sticker.emoji}"

        if message.text is not None:
            self._text_repr += f"\n{message.text}"

        if message.caption is not None:
            self._text_repr += f"\n{message.caption}"

    def _save_file(self,obj:any) -> str:
        try:
            if not hasattr(obj,"file_id"):
                raise(Exception("object has no file_id attribute"))

            # get data
            file_info = self._bot.get_file(obj.file_id)

            # create name
            file_name = ""
            if hasattr(obj,"file_name"):
                if obj.file_name is not None:
                    file_name = obj.file_name

            if file_name == "":
                ext = file_info.file_path.split(".")[-1]
                file_name = file_info.file_unique_id +"."+ ext

            # make path
            path_string = self._storage_path + file_name

            # get file
            file_data = self._bot.download_file(file_info.file_path)

            # save file
            path = Path(path_string)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as f:
                f.write(file_data)

            return path_string
        except Exception as _:
            # TODO: log this shit
            return "file is not saved"

    def text(self) -> str:
        return self._text_repr

    def image(self) -> str:
        return self._image_data

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

        draft = "\n\n".join(self._text_drafts)

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

            # TODO: log this shit
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
        self._chat_id = chat_id
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
        if not self._is_typing:
            self._typing_thread.start()
            self._is_typing = True

    def stop_typing(self):
        if self._is_typing:
            self._stop_typing_ev.set()
            self._typing_thread.join()
            self._is_typing = False

    def __enter__(self) -> "TypingAction":
        self.start_typing()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop_typing()

