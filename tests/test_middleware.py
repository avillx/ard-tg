import logging
import unittest.mock

from telebot.handler_backends import CancelUpdate

from telegram.middleware import (
    LoggingMiddleware,
    UserContactKeeper,
    UserWhitelistMiddleware,
    _extract_chat_id,
)


class _Chat:
    def __init__(self, chat_id: int, first_name: str = "") -> None:
        self.id = chat_id
        self.first_name = first_name


class _FromUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class _Message:
    # chat/from_user deliberately absent on some messages: the middleware tests
    # exercise hasattr() paths, so they are only set in mkmessage().
    chat: _Chat  # pyright: ignore[reportUninitializedInstanceVariable]
    from_user: _FromUser  # pyright: ignore[reportUninitializedInstanceVariable]


def mkmessage(
    chat_id: int | None = None,
    from_id: int | None = None,
    first_name: str = "",
) -> _Message:
    obj = _Message()
    if chat_id is not None:
        obj.chat = _Chat(chat_id, first_name)
    if from_id is not None:
        obj.from_user = _FromUser(from_id)
    return obj


def test_extract_chat_id_from_chat() -> None:
    assert _extract_chat_id(mkmessage(chat_id=55)) == 55


def test_extract_chat_id_prefers_chat_over_user() -> None:
    assert _extract_chat_id(mkmessage(chat_id=55, from_id=99)) == 55


def test_extract_chat_id_from_user() -> None:
    assert _extract_chat_id(mkmessage(from_id=77)) == 77


def test_extract_chat_id_empty() -> None:
    assert _extract_chat_id(_Message()) == 0


def test_whitelist_allows_known_chat(logger: logging.Logger) -> None:
    mw = UserWhitelistMiddleware(allowed_chats=[1, 2], logger=logger)

    assert mw.pre_process(mkmessage(chat_id=1), {}) is None


def test_whitelist_blocks_unknown_chat(logger: logging.Logger) -> None:
    mw = UserWhitelistMiddleware(allowed_chats=[1, 2], logger=logger)

    result = mw.pre_process(mkmessage(chat_id=3), {})

    assert isinstance(result, CancelUpdate)


def test_contact_keeper_adds_new_contact(logger: logging.Logger) -> None:
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {}
    mw = UserContactKeeper(contact_svc)

    mw.pre_process(mkmessage(chat_id=55, first_name="Alice"), {})

    contact_svc.add_contact.assert_called_once_with("55", "Alice")


def test_contact_keeper_skips_existing_contact(logger: logging.Logger) -> None:
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {"55": "Alice"}
    mw = UserContactKeeper(contact_svc)

    mw.pre_process(mkmessage(chat_id=55), {})

    contact_svc.add_contact.assert_not_called()


def test_contact_keeper_empty_name_without_chat(logger: logging.Logger) -> None:
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {}
    mw = UserContactKeeper(contact_svc)

    # no chat attribute on the message, so chat_id becomes "0" and the name stays empty
    mw.pre_process(_Message(), {})

    contact_svc.add_contact.assert_called_once_with("0", "")


def test_logging_middleware_smoke(logger: logging.Logger) -> None:
    mw = LoggingMiddleware(logger)

    mw.pre_process(mkmessage(chat_id=55), {})
    mw.post_process(mkmessage(chat_id=55), {}, None)
    mw.post_process(mkmessage(chat_id=55), {}, Exception("x"))

    assert "message" in mw.update_types
