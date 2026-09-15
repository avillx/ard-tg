import telebot
import telebot.types as telebot_types


class Attachment:
    _bot: telebot.TeleBot
    _file_id: str
    _file_info: telebot_types.File | None
    _bytes: bytes | None
    _file_name_base: str

    def __init__(
        self,
        bot: telebot.TeleBot,
        obj: telebot_types.PhotoSize
        | telebot_types.Audio
        | telebot_types.Video
        | telebot_types.VideoNote
        | telebot_types.Document
        | telebot_types.Voice,
    ) -> None:

        self._bot = bot
        self._file_id = obj.file_id
        self._file_name_base = "attachment"
        self._file_info = None
        self._bytes = None

        # object can has no attribute, well then name will have only uuid
        file_name = getattr(obj, "file_name", None)
        if isinstance(file_name, str):
            self._file_name_base = file_name

    def get_bytes(self) -> bytes:
        """
        Download file and return raw file bytes. if it already downloaded then
        just return already downloaded bytes
        """
        if self._bytes is None:
            file_info = self._get_file_info()
            if file_info.file_path is None:
                raise Exception("file_info has no file_path, can't download bytes")
            self._bytes = self._bot.download_file(file_info.file_path)

        return self._bytes

    def get_file_name(self) -> str:
        """
        Get detailed file info and builds unique file name with file extension
        """
        file_info = self._get_file_info()
        if file_info.file_path is None:
            raise Exception("file_info has no file_path")

        ext = file_info.file_path.split(".")[-1]

        return f"{self._file_name_base}_{file_info.file_unique_id}.{ext}"

    def _get_file_info(self) -> telebot_types.File:
        """
        Get file info from telegram
        """
        if self._file_info is None:
            file_info = self._bot.get_file(self._file_id)
            if file_info.file_path is None:
                raise Exception("telegram return no path to file")
            self._file_info = file_info

        return self._file_info


def extract_attachments(bot: telebot.TeleBot, msg: telebot_types.Message) -> list[Attachment]:

    attachments: list[Attachment] = []

    if msg.photo is not None:
        attachments.append(Attachment(bot, msg.photo[-1]))

    if msg.audio is not None:
        attachments.append(Attachment(bot, msg.audio))

    if msg.video is not None:
        attachments.append(Attachment(bot, msg.video))

    if msg.video_note is not None:
        attachments.append(Attachment(bot, msg.video_note))

    if msg.document is not None:
        attachments.append(Attachment(bot, msg.document))

    if msg.voice is not None:
        attachments.append(Attachment(bot, msg.voice))

    return attachments
