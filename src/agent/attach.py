from abc import ABC, abstractmethod
lazy import logging

from agent.session import SessionDefiner, SuperfluousSetSessionError


class MessangerBot(ABC):
    @abstractmethod
    def send(self,chat_id: int, message: str):
        pass

class AttachService:
    """Serve attaching an agent session to a chat from an external invocation

    e.g. an agent wants to initiate contact with the user from autonomous mode
    """
    _session_definer: SessionDefiner
    _messanger_bot: MessangerBot
    _logger: logging.Logger

    def __init__(
        self,
        session_definer: SessionDefiner,
        messanger_bot: MessangerBot,
        logger: logging.Logger,
    ):
        self._session_definer = session_definer
        self._logger = logger.getChild("Attach")
        self._messanger_bot = messanger_bot

    def attach(self, session_id: str, chat_id: int, message: str, await_time: float) -> None:
        try:
            self._session_definer.set_session_id(session_id=session_id, additional_time=await_time)
        except SuperfluousSetSessionError as err:
            raise Exception("Session attach is superfluous. Messages already received") from err

        try:
            self._messanger_bot.send(chat_id,message)
        except Exception as err:
            self._logger.error(
                "send attachment message is failed. session: %s. chat: %s. error: %s", session_id, chat_id,err
            )
            raise Exception("gateway has problem. message is not sended") from err

        self._logger.info("session %s attached to chat %s", session_id, chat_id)
