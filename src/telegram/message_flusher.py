import os
from datetime import datetime
from pathlib import Path
from typing import Any

import telebot
import telebot.types as telebot_types


class MessageFlusher:
    _text_repr: str
    _image_data: str
    _bot: telebot.TeleBot
    _storage_path: str

    def __init__(
        self,
        bot: telebot.TeleBot,
        message: telebot_types.Message,
        storage_path: str,
    ):
        self._storage_path = os.path.join(storage_path, "uploads")
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

    def _save_file(self, obj: Any) -> str:
        try:
            if not hasattr(obj, "file_id"):
                raise (Exception("object has no file_id attribute"))

            # get data
            file_info = self._bot.get_file(obj.file_id)
            if file_info.file_path is None:
                raise Exception("telegram return no path to file")

            # create name
            file_name = ""
            if hasattr(obj, "file_name") and obj.file_name is not None:
                file_name = obj.file_name

            if file_name == "":
                file_name = file_info.file_unique_id

            ext = file_info.file_path.split(".")[-1]
            file_name += "." + ext

            # make path
            path_string = os.path.join(self._storage_path, file_name)

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
