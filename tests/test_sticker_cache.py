import unittest.mock

import pytest
from telebot import types as telebot_types

from telegram.sticker_cache import StickerCache


def _sticker(emoji, file_id):
    return telebot_types.Sticker(
        file_id=file_id,
        file_unique_id="u" + file_id,
        type="regular",
        width=512,
        height=512,
        is_animated=False,
        is_video=False,
        emoji=emoji,
    )


def _sticker_set(*stickers):
    return telebot_types.StickerSet(name="pack", title="P", sticker_type="regular", stickers=list(stickers))


def test_get_pack_from_bot(logger):
    bot = unittest.mock.Mock()
    bot.get_sticker_set.return_value = _sticker_set(_sticker("😀", "f1"), _sticker("🐱", "f2"))
    cache = StickerCache(bot=bot, logger=logger)

    assert cache.get_pack("pack") == {"😀": "f1", "🐱": "f2"}
    bot.get_sticker_set.assert_called_once_with("pack")


def test_get_pack_is_cached(logger):
    bot = unittest.mock.Mock()
    bot.get_sticker_set.return_value = _sticker_set(_sticker("😀", "f1"))
    cache = StickerCache(bot=bot, logger=logger)

    cache.get_pack("pack")
    cache.get_pack("pack")

    assert bot.get_sticker_set.call_count == 1


def test_get_pack_skips_stickers_without_emoji(logger):
    bot = unittest.mock.Mock()
    bot.get_sticker_set.return_value = _sticker_set(_sticker(None, "f1"), _sticker("😀", "f2"))
    cache = StickerCache(bot=bot, logger=logger)

    assert cache.get_pack("pack") == {"😀": "f2"}


def test_get_pack_missing_raises(logger):
    bot = unittest.mock.Mock()
    bot.get_sticker_set.return_value = None
    cache = StickerCache(bot=bot, logger=logger)

    with pytest.raises(Exception, match="pack"):
        cache.get_pack("pack")