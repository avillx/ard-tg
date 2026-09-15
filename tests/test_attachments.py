import unittest.mock
from typing import Any

import pytest
import telebot.types as telebot_types

from telegram.attachments import Attachment, extract_attachments


def _message(**options: Any) -> telebot_types.Message:
    return telebot_types.Message(
        message_id=1,
        from_user=None,
        date=123,
        chat=telebot_types.Chat(id=55, type="private", first_name="Alice"),
        content_type="text",
        options=options,
        json_string="{}",
    )


def _bot_with_file(file_id: str, unique_id: str, path: str | None) -> unittest.mock.Mock:
    bot = unittest.mock.Mock()
    bot.get_file.return_value = telebot_types.File(
        file_id=file_id, file_unique_id=unique_id, file_path=path
    )
    bot.download_file.return_value = b"data"
    return bot


def _bot_for(files: dict[str, tuple[str, str]]) -> unittest.mock.Mock:
    bot = unittest.mock.Mock()

    def get_file(file_id: str) -> telebot_types.File:
        unique_id, path = files[file_id]
        return telebot_types.File(file_id=file_id, file_unique_id=unique_id, file_path=path)

    bot.get_file.side_effect = get_file
    return bot


def test_get_file_name_uses_unique_id_and_extension() -> None:
    bot = _bot_with_file("F1", "U1", "docs/report.pdf")
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)

    assert Attachment(bot, photo).get_file_name() == "attachment_U1.pdf"


def test_get_file_name_uses_document_file_name() -> None:
    bot = _bot_with_file("D1", "DU1", "docs/du1.jpg")
    doc = telebot_types.Document(file_id="D1", file_unique_id="DU1", file_name="report")

    assert Attachment(bot, doc).get_file_name() == "report_DU1.jpg"


def test_get_bytes_downloads_once_and_caches() -> None:
    bot = _bot_with_file("F1", "U1", "photos/p.jpg")
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)
    att = Attachment(bot, photo)

    assert att.get_bytes() == b"data"
    assert att.get_bytes() == b"data"
    bot.download_file.assert_called_once_with("photos/p.jpg")


def test_get_file_info_is_cached() -> None:
    bot = _bot_with_file("F1", "U1", "photos/p.jpg")
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)
    att = Attachment(bot, photo)

    att.get_file_name()
    att.get_bytes()

    bot.get_file.assert_called_once_with("F1")


def test_get_file_name_raises_without_file_path() -> None:
    bot = _bot_with_file("F1", "U1", None)
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)

    with pytest.raises(Exception, match="no path"):
        Attachment(bot, photo).get_file_name()


def test_get_bytes_raises_without_file_path() -> None:
    bot = _bot_with_file("F1", "U1", None)
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)

    with pytest.raises(Exception, match="no path"):
        Attachment(bot, photo).get_bytes()


def test_extract_attachments_empty_message() -> None:
    assert extract_attachments(bot=unittest.mock.Mock(), msg=_message()) == []


def test_extract_attachments_uses_largest_photo() -> None:
    small = telebot_types.PhotoSize(file_id="P1", file_unique_id="PU1", width=10, height=10)
    large = telebot_types.PhotoSize(file_id="P2", file_unique_id="PU2", width=100, height=100)
    bot = _bot_for({"P2": ("PU2", "photos/p2.jpg")})

    atts = extract_attachments(bot=bot, msg=_message(photo=[small, large]))

    # photo list items are ordered small -> large, so the last one is kept
    assert len(atts) == 1
    assert atts[0].get_file_name() == "attachment_PU2.jpg"
    bot.get_file.assert_called_once_with("P2")


def test_extract_attachments_returns_each_media_kind() -> None:
    msg = _message(
        audio=telebot_types.Audio(file_id="A1", file_unique_id="AU1", duration=1),
        video=telebot_types.Video(
            file_id="V1", file_unique_id="VU1", width=1, height=1, duration=1
        ),
        video_note=telebot_types.VideoNote(
            file_id="VN1", file_unique_id="VNU1", length=1, duration=1
        ),
        document=telebot_types.Document(file_id="D1", file_unique_id="DU1"),
        voice=telebot_types.Voice(file_id="VO1", file_unique_id="VOU1", duration=1),
    )
    bot = _bot_for(
        {
            "A1": ("AU1", "audio/a1.mp3"),
            "V1": ("VU1", "video/v1.mp4"),
            "VN1": ("VNU1", "video_notes/vn1.mp4"),
            "D1": ("DU1", "docs/d1.pdf"),
            "VO1": ("VOU1", "voice/vo1.ogg"),
        }
    )

    atts = extract_attachments(bot=bot, msg=msg)

    assert [att.get_file_name() for att in atts] == [
        "attachment_AU1.mp3",
        "attachment_VU1.mp4",
        "attachment_VNU1.mp4",
        "attachment_DU1.pdf",
        "attachment_VOU1.ogg",
    ]
