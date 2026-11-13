import logging
import threading
import time
from abc import ABC, abstractmethod

import ard.api.sessions.create_session as create_session
import ard.client as agent_client
import ard.models as models

_DEFAULT_SESSION_TTL: float = 600


class SuperfluousSetSessionError(Exception):
    pass


class TimeProvider(ABC):
    @abstractmethod
    def now(self) -> float:
        pass


class SystemTime(TimeProvider):
    def now(self) -> float:
        return time.monotonic()


class SessionService:
    """
    Sevice with session manage responsobility
    """

    _agent_id: str
    _agent_client: agent_client.Client
    _actual_session: str
    _last_update: float
    _life_time: float
    _instruction: str
    _logger: logging.Logger
    _mutex = threading.Lock()
    _additional_time: float
    _time: TimeProvider

    def __init__(
        self,
        agent_id: str,
        agent_client: agent_client.Client,
        life_time: float,
        instruction: str,
        logger: logging.Logger,
        time: TimeProvider,
    ):
        self._logger = logger.getChild("Sessions")
        self._agent_client = agent_client
        self._life_time = life_time
        self._agent_id = agent_id
        self._last_update = 0.0
        self._actual_session = ""
        self._mutex = threading.Lock()
        self._instruction = instruction
        self._additional_time = 0.0
        self._time = time

    def drop(self):
        """
        Drops current session and set it to None
        """
        with self._mutex:
            self._actual_session = ""

    def set(self, session_id: str, additional_time: float = 0.0):
        """
        Set session id as actual session. addiational time to live for setted session
        """
        if self._is_actual() and session_id == self.get():
            raise SuperfluousSetSessionError()

        with self._mutex:
            self._additional_time = additional_time
            self._last_update = self._time.now()
            self._actual_session = session_id

    def get(self) -> str:
        """
        Return current setted session
        """
        with self._mutex:
            return self._actual_session

    def get_actual(self) -> str:
        """
        Get session, if session expires or is None then creates a new
        """
        with self._mutex:
            # is expired or empty

            actual_session_is_unset = self._actual_session == ""
            actual_session_is_expires = not self._is_actual()

            if actual_session_is_unset or actual_session_is_expires:
                self._actual_session = self._create_new_session()

            self._last_update = self._time.now()
            self._additional_time = 0.0  # set zero cause last_time is upddated.
            return self._actual_session

    def _is_actual(self) -> bool:
        now = self._time.now()
        idle_time = now - (self._additional_time + self._last_update)
        return idle_time <= self._life_time

    def _create_new_session(self, additional_time: float = 0.0) -> str:
        """
        Make request to agent to create a new system and return id on created session
        """
        self._additional_time = additional_time

        create_session_request = models.CreateSessionBody(
            instruction=self._instruction,
        )

        resp = create_session.sync(
            self._agent_id,
            client=self._agent_client,
            body=create_session_request,
        )

        match resp:
            case None:
                raise Exception("agent return no session")

            case models.ValidationError():
                raise Exception(f"problem with session: {resp.problems}")

            case models.Error():
                raise Exception(f"problem with session: {resp.message}")

            case models.CreateSessionResponse200():
                self._logger.info(f"created new session with id: {resp.id}")
                return resp.id
