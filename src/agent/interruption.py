from abc import ABC, abstractmethod
lazy import logging

import agent.session as session
import ard.api.chat.interrupt_chat as interrupt_chat
import ard.client as agent_client


class Interruptor(ABC):
    @abstractmethod
    def interrupt(self) -> None:
        pass

class InterruptionService:
    _session_source: session.SessionSource
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        session_source: session.SessionSource,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._session_source = session_source
        self._logger = logger
        self._agent_client = client

    def interrupt(self) -> None:
        """Interrupt the agent session in progress."""
        session_id = self._session_source.get_session_id()
        self._logger.info("interrupting, session: %s", session_id)

        _ = interrupt_chat.sync_detailed(
            session=session_id,
            client=self._agent_client,
        )
