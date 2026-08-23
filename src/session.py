import logging
import threading
import time

import arch_agent.api.sessions.create_session as create_session
import arch_agent.client as agent_client
import arch_agent.models as models


class SessionService:
    _agent_id: str
    _agent_client: agent_client.Client
    _actual_session: str
    _last_update: float
    _life_time: float
    _logger: logging.Logger
    _mutex = threading.Lock()

    def __init__(
            self,
            agent_id: str,
            agent_client: agent_client.Client,
            life_time: float,
            logger: logging.Logger,
        ):
        self._logger = logger.getChild("Sessions")
        self._agent_client = agent_client
        self._life_time = life_time
        self._agent_id = agent_id
        self._last_update = 0
        self._actual_session = ""
        self._mutex = threading.Lock()

    def get_current(self) -> str:
        with self._mutex:
            return self._actual_session

    def get_actual_session(self) -> str:
        with self._mutex:
            now = time.monotonic()

            # is expired
            if now - self._last_update > self._life_time:
                self._actual_session = self.create_new_session()
                self._last_update = now

            return self._actual_session

    def create_new_session(self) -> str:

        create_session_request = models.CreateSessionBody(instruction="")

        resp = create_session.sync(
            self._agent_id,
            client=self._agent_client,
            body=create_session_request,
        )
        if resp is None:
            self._logger.error("agent return empty session")
            return ""

        self._logger.info(f"created new session with id: {resp.id}")
        return resp.id
