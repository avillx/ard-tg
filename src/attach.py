
import logging

import telebot

import session


class AttachService:
    """
    Serve to attach agent session to chat with external invoke.
    e.g. Agent want self initiate contact with user. from autonomus mode
    """

    _session_service : session.SessionService
    _bot : telebot.TeleBot
    _logger : logging.Logger

    def __init__(
            self, session_service : session.SessionService,
            bot : telebot.TeleBot,
            logger : logging.Logger,
        ):
        self._session_service : session.SessionService = session_service
        self._bot : telebot.TeleBot = bot
        self._logger : logging.Logger = logger.getChild("Attach")

    def attach(
            self,session_id: str,
            chat_id: str,
            message: str,
            await_time: float
        ) -> None:

        self._session_service.set_session(
                session_id=session_id,
                additional_time=await_time
            )

        input = telebot.types.InputRichMessage(
            markdown=message
        )

        self._bot.send_rich_message(
            chat_id=chat_id,
            rich_message=input,
        )

        self._logger.info(f"session {session_id} attached to chat {chat_id}")
