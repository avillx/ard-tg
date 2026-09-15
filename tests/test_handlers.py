from typing import Any

import telebot.types as telebot_types

from telegram.handlers import represent_message


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


def test_represent_text_message() -> None:
    text = represent_message(_message(text="привет"), [])

    assert text.startswith("# From Alice (")
    assert text.endswith("\nпривет")


def test_represent_empty_message_has_only_header() -> None:
    text = represent_message(_message(), [])

    assert text.startswith("# From Alice (")
    assert "\n" not in text


def test_represent_caption_and_sticker() -> None:
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

    text = represent_message(_message(caption="cap", sticker=sticker), [])

    assert "\ncap" in text
    assert "\nSticker: 😀" in text


def test_represent_appends_additional_lines() -> None:
    text = represent_message(_message(), ["one", "two"])

    assert text.endswith("\none\ntwo")
