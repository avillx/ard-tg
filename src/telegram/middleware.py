from typing import override
lazy import logging

from telebot.handler_backends import BaseMiddleware, CancelUpdate

from telegram.tools import telebot_types
lazy import contacts


class LoggingMiddleware(BaseMiddleware):
    _log: logging.Logger

    def __init__(self, logger: logging.Logger):
        super().__init__()
        self._log = logger.getChild("Telegram")
        self.update_types: list[str] = ["message", "chosen_inline_result", "chat_join_request"]

    @override
    def pre_process(self, message: telebot_types.Message, data):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]
        chat_id = _extract_chat_id(message)
        self._log.info("update in chat: %s", chat_id)

    @override
    def post_process(self, message: telebot_types.Message, data, exception: Exception):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]
        if exception:
            chat_id = _extract_chat_id(message)
            self._log.error("in chat: %s, cause %s", chat_id, exception)


class UserWhitelistMiddleware(BaseMiddleware):
    _allowed_chats: list[int]
    _log: logging.Logger

    def __init__(self, allowed_chats: list[int], logger: logging.Logger):
        super().__init__()
        self.update_types: list[str] = ["message", "chosen_inline_result", "chat_join_request"]
        self._allowed_chats = allowed_chats
        self._log = logger.getChild("white list")

    @override
    def pre_process(self, message: telebot_types.Message, data):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]

        chat_id = _extract_chat_id(message)
        if chat_id not in self._allowed_chats:
            self._log.warning("update from unallowed chat '%s' ignored", chat_id)
            return CancelUpdate()
        return None

    @override
    def post_process(self, message: telebot_types.Message, data, exception: Exception):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]
        pass


class UserContactKeeper(BaseMiddleware):
    _contact_service: contacts.ContactService

    def __init__(self, contact_service: contacts.ContactService):
        super().__init__()
        self.update_types: list[str] = ["message", "chosen_inline_result", "chat_join_request"]
        self._contact_service = contact_service

    @override
    def pre_process(self, message: telebot_types.Message, data):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]
        chat_id = _extract_chat_id(message)
        if self._contact_service.contacts().get(str(chat_id)):
            return

        name = ""
        if hasattr(message, "chat") and message.chat.first_name:
            name = message.chat.first_name

        self._contact_service.add_contact(str(chat_id), name)

    @override
    def post_process(self, message: telebot_types.Message, data, exception: Exception):  # pyright: ignore[reportMissingParameterType,reportUnknownParameterType]
        pass


def _extract_chat_id(message: telebot_types.Message) -> int:
    if hasattr(message, "chat"):
        return message.chat.id
    if hasattr(message, "from_user") and message.from_user:
        return message.from_user.id
    return 0
