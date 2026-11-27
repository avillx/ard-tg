from typing import override
lazy import logging

import ard.api.chat.interrupt_chat as interrupt_chat
import ard.client as agent_client
from domain.interruption import Interruptor


class AgentAPIInterruption(Interruptor):
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    @override
    def interrupt(self,session_id:str) -> None:
        """Interrupt the agent session in progress."""
        self._logger.info("interrupting, session: %s", session_id)

        _ = interrupt_chat.sync_detailed(
            session=session_id,
            client=self._agent_client,
        )
