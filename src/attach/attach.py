lazy import logging

import telebot
import telebot.types as telebot_types

import agent


class AttachService:
    """Serve attaching an agent session to a chat from an external invocation

    e.g. an agent wants to initiate contact with the user from autonomous mode
    """

    def __init__(
        self,
        session_service: agent.SessionService,
        bot: telebot.TeleBot,
        logger: logging.Logger,
    ):
        self._session_service: agent.SessionService = session_service
        self._bot: telebot.TeleBot = bot
        self._logger: logging.Logger = logger.getChild("Attach")

    def attach(self, session_id: str, chat_id: int, message: str, await_time: float) -> None:

        try:
            self._session_service.set(session_id=session_id, additional_time=await_time)
        except agent.SuperfluousSetSessionError as err:
            raise Exception("Session attach is superfluous. Messages already received") from err

        rich_message = telebot_types.InputRichMessage(markdown=message)

        self._bot.send_rich_message(
            chat_id=chat_id,
            rich_message=rich_message,
        )

        self._logger.info("session %s attached to chat %s", session_id, chat_id)
