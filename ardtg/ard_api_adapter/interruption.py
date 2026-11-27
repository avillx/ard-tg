from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.chat import interrupt_chat
from ardtg.domain.interruption import Interruptor

if TYPE_CHECKING:
    import logging

    from ardtg.ard_api import Client

class AgentAPIInterruption(Interruptor):
    _logger: logging.Logger
    _client: Client

    def __init__(
        self,
        client: Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._client = client

    @override
    def interrupt(self,session_id:str) -> None:
        """Interrupt the agent session in progress."""
        self._logger.info("interrupting, session: %s", session_id)

        _ = interrupt_chat.sync_detailed(
            session=session_id,
            client=self._client,
        )
