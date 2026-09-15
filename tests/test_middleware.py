import unittest.mock

from telebot.handler_backends import CancelUpdate

from telegram.middleware import (
    LoggingMiddleware,
    UserContactKeeper,
    UserWhitelistMiddleware,
    _extract_chat_id,
)


class _Chat:
    def __init__(self, chat_id, first_name=""):
        self.id = chat_id
        self.first_name = first_name


class _FromUser:
    def __init__(self, user_id):
        self.id = user_id


class _Empty:
    pass


def mkmessage(chat_id=None, from_id=None, first_name=""):
    obj = _Empty()
    if chat_id is not None:
        obj.chat = _Chat(chat_id, first_name)
    if from_id is not None:
        obj.from_user = _FromUser(from_id)
    return obj


# ---------------------------------------------------------------------------
# _extract_chat_id
# ---------------------------------------------------------------------------


def test_extract_chat_id_from_chat():
    assert _extract_chat_id(mkmessage(chat_id=55)) == 55


def test_extract_chat_id_prefers_chat_over_user():
    assert _extract_chat_id(mkmessage(chat_id=55, from_id=99)) == 55


def test_extract_chat_id_from_user():
    assert _extract_chat_id(mkmessage(from_id=77)) == 77


def test_extract_chat_id_empty():
    assert _extract_chat_id(_Empty()) == 0


# ---------------------------------------------------------------------------
# UserWhitelistMiddleware
# ---------------------------------------------------------------------------


def test_whitelist_allows_known_chat(logger):
    mw = UserWhitelistMiddleware(allowed_chats=[1, 2], logger=logger)

    assert mw.pre_process(mkmessage(chat_id=1), {}) is None


def test_whitelist_blocks_unknown_chat(logger):
    mw = UserWhitelistMiddleware(allowed_chats=[1, 2], logger=logger)

    result = mw.pre_process(mkmessage(chat_id=3), {})

    assert isinstance(result, CancelUpdate)


# ---------------------------------------------------------------------------
# UserContactKeeper
# ---------------------------------------------------------------------------


def test_contact_keeper_adds_new_contact(logger):
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {}
    mw = UserContactKeeper(contact_svc)

    mw.pre_process(mkmessage(chat_id=55, first_name="Alice"), {})

    contact_svc.add_contact.assert_called_once_with("55", "Alice")


def test_contact_keeper_skips_existing_contact(logger):
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {"55": "Alice"}
    mw = UserContactKeeper(contact_svc)

    mw.pre_process(mkmessage(chat_id=55), {})

    contact_svc.add_contact.assert_not_called()


def test_contact_keeper_empty_name_without_chat(logger):
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {}
    mw = UserContactKeeper(contact_svc)

    # no chat -> no way to extract chat_id -> name stays "" and id is "0"
    mw.pre_process(_Empty(), {})

    contact_svc.add_contact.assert_called_once_with("0", "")


# ---------------------------------------------------------------------------
# LoggingMiddleware
# ---------------------------------------------------------------------------


def test_logging_middleware_smoke(logger):
    mw = LoggingMiddleware(logger)

    mw.pre_process(mkmessage(chat_id=55), {})
    mw.post_process(mkmessage(chat_id=55), {}, None)
    mw.post_process(mkmessage(chat_id=55), {}, Exception("x"))

    assert "message" in mw.update_types