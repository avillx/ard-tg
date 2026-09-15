import os
import unittest.mock

from telebot import types as telebot_types

from telegram.message_flusher import MessageFlusher


def make_message(**options) -> telebot_types.Message:
    return telebot_types.Message(
        message_id=1,
        from_user=None,
        date=123,
        chat=telebot_types.Chat(id=55, type="private", first_name="Alice"),
        content_type="text",
        options=options,
        json_string="{}",
    )


def test_text_only(tmp_path):
    f = MessageFlusher(bot=unittest.mock.Mock(), message=make_message(text="привет"), storage_path=str(tmp_path))

    text = f.text()

    assert text.startswith("# From Alice (")
    assert text.endswith("\nпривет")


def test_empty_message_has_only_prefix(tmp_path):
    f = MessageFlusher(bot=unittest.mock.Mock(), message=make_message(), storage_path=str(tmp_path))

    text = f.text()

    assert text.startswith("# From Alice (")
    assert "\n" not in text


def test_text_and_caption(tmp_path):
    f = MessageFlusher(
        bot=unittest.mock.Mock(),
        message=make_message(text="hello", caption="cap"),
        storage_path=str(tmp_path),
    )

    text = f.text()

    assert "\nhello" in text
    assert "\ncap" in text


def test_photo_saves_file(tmp_path):
    bot = unittest.mock.Mock()
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)
    bot.get_file.return_value = telebot_types.File(file_id="F1", file_unique_id="U1", file_path="photos/u1.jpg")
    bot.download_file.return_value = b"JPEGDATA"

    f = MessageFlusher(bot=bot, message=make_message(photo=[photo]), storage_path=str(tmp_path))

    text = f.text()

    assert f"Photo saved on path: {os.path.join('telegram', 'uploads', 'U1.jpg')}" in text
    saved = tmp_path / "uploads" / "telegram" / "uploads" / "U1.jpg"
    assert saved.read_bytes() == b"JPEGDATA"


def test_document_uses_filename(tmp_path):
    bot = unittest.mock.Mock()
    doc = telebot_types.Document(file_id="D1", file_unique_id="DU1", file_name="report")
    bot.get_file.return_value = telebot_types.File(file_id="D1", file_unique_id="DU1", file_path="docs/du1.pdf")
    bot.download_file.return_value = b"PDF"

    f = MessageFlusher(bot=bot, message=make_message(document=doc), storage_path=str(tmp_path))

    assert f"Document saved on path: {os.path.join('telegram', 'uploads', 'report.pdf')}" in f.text()


def test_sticker_emoji(tmp_path):
    sticker = telebot_types.Sticker(
        file_id="S1",
        file_unique_id="SU1",
        type="regular",
        width=512,
        height=512,
        is_animated=False,
        is_video=False,
        emoji="😀",
    )

    f = MessageFlusher(bot=unittest.mock.Mock(), message=make_message(sticker=sticker), storage_path=str(tmp_path))

    assert "Sticker: 😀" in f.text()


def test_save_file_failure_produces_placeholder(tmp_path):
    bot = unittest.mock.Mock()
    photo = telebot_types.PhotoSize(file_id="F1", file_unique_id="U1", width=10, height=10)
    bot.get_file.return_value = telebot_types.File(file_id="F1", file_unique_id="U1", file_path=None)

    f = MessageFlusher(bot=bot, message=make_message(photo=[photo]), storage_path=str(tmp_path))

    assert "Photo saved on path: file is not saved" in f.text()