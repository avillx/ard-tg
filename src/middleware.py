import logging

from telebot.handler_backends import BaseMiddleware, CancelUpdate

import contacts


class LoggingMiddleware(BaseMiddleware):
    _log : logging.Logger

    def __init__(self, logger: logging.Logger):
        self._log = logger.getChild("Telegram")
        self.update_types = ["message", "chosen_inline_result", "chat_join_request"]

    def pre_process(self, message, data):
        chat_id = _extract_chat_id(message)
        self._log.info(f"update in chat: {chat_id}")

    def post_process(self, message, data, exception):
            if exception is not None:
                chat_id = _extract_chat_id(message)
                self._log.error(f"in chat: {chat_id}, cause {exception}")

class UserWhitelistMiddleware(BaseMiddleware):
    _allowed_chats : list[int]
    _log : logging.Logger

    def __init__(self, allowed_chats: list[int], logger: logging.Logger):
        self.update_types = ["message", "chosen_inline_result", "chat_join_request"]
        self._allowed_chats = allowed_chats
        self._log = logger.getChild("white list")

    def pre_process(self, message, data):
        chat_id = _extract_chat_id(message)
        if chat_id not in self._allowed_chats:
            self._log.warning(f"update from unallowed chat '{chat_id}' ignored")
            return CancelUpdate()

    def post_process(self, message, data, exception):
        pass

def _extract_chat_id( message) -> int:
    if hasattr(message, "chat"):
        return message.chat.id
    if hasattr(message, "from_user"):
        return message.from_user.id
    return 0


class UserContactKeeper(BaseMiddleware):
    _contact_service: contacts.ContactService

    def __init__(self, contact_service: contacts.ContactService):
        self.update_types: list[str] = ["message", "chosen_inline_result", "chat_join_request"]
        self._contact_service = contact_service


    def pre_process(self, message, data):
        chat_id = _extract_chat_id(message)
        if self._contact_service.contacts().get(str(chat_id)):
            return

        name = ""
        if hasattr(message, "chat"):
            name = message.chat.first_name

        self._contact_service.add_contact(str(chat_id), name)

    def post_process(self, message, data, exception):
        pass

def _extract_chat_id( message) -> int:
    if hasattr(message, "chat"):
        return message.chat.id
    if hasattr(message, "from_user"):
        return message.from_user.id
    return 0
