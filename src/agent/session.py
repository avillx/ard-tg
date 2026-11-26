import threading
import time
from abc import ABC, abstractmethod
from typing import override
lazy import logging

DEFAULT_SESSION_TTL: float = 600


class SuperfluousSetSessionError(Exception):
    pass

class SessionDropper(ABC):
    @abstractmethod
    def drop(self) -> None:
        pass

class SessionDefiner(ABC):
    @abstractmethod
    def set_session_id(self, session_id: str, additional_time: float = 0.0) -> None:
        pass

class SessionRepo(ABC):
    @abstractmethod
    def new_session(self,profile_id: str, instruction: str) -> str:
        pass

class SessionSource(ABC):
    @abstractmethod
    def get_session_id(self) -> str:
        pass

    @abstractmethod
    def get_unexpired_session_id(self) -> str:
        pass

class ProfileSource(ABC):
    @abstractmethod
    def get_profile(self) -> str:
        pass


class TimeProvider(ABC):
    @abstractmethod
    def now(self) -> float:
        pass


class SystemTime(TimeProvider):
    @override
    def now(self) -> float:
        return time.monotonic()


class SessionService(SessionSource,SessionDefiner,SessionDropper):
    """Service with session management responsibility."""

    _profile_id: str
    _profile_source: ProfileSource
    _session_repo: SessionRepo
    _actual_session: str
    _last_update: float
    _life_time: float
    _instruction: str
    _logger: logging.Logger
    _mutex: threading.Lock = threading.Lock()
    _additional_time: float
    _time: TimeProvider

    def __init__(
        self,
        profile_source: ProfileSource,
        life_time: float,
        instruction: str,
        logger: logging.Logger,
        session_repo: SessionRepo,
        time: TimeProvider,
    ):
        self._logger = logger.getChild("Sessions")
        self._session_repo = session_repo
        self._life_time = life_time
        self._profile_id = profile_source.get_profile()
        self._last_update = 0.0
        self._actual_session = ""
        self._mutex = threading.Lock()
        self._instruction = instruction
        self._additional_time = 0.0
        self._time = time
        self._profile_source = profile_source

    @override
    def drop(self):
        """Drop the current session and set it to None."""
        with self._mutex:
            self._actual_session = ""

    @override
    def set_session_id(self, session_id: str, additional_time: float = 0.0):
        """Set the session id as the actual session

        additional_time extends the time to live of the set session
        """
        if self._is_actual() and session_id == self.get_session_id():
            raise SuperfluousSetSessionError()

        with self._mutex:
            self._additional_time = additional_time
            self._last_update = self._time.now()
            self._actual_session = session_id

    @override
    def get_session_id(self) -> str:
        """Return the currently set session."""
        with self._mutex:
            return self._actual_session

    @override
    def get_unexpired_session_id(self) -> str:
        """Get the session, creating a new one when it is unset or expired."""
        with self._mutex:
            profile_is_actual = self._profile_source.get_profile() == self._profile_id
            actual_session_is_unset = self._actual_session == ""
            actual_session_is_expires = not self._is_actual()

            if actual_session_is_unset or actual_session_is_expires or not profile_is_actual:
                self._new_session()

            self._last_update = self._time.now()
            self._additional_time = 0.0  # set zero cause last_time is upddated.
            return self._actual_session

    def _is_actual(self) -> bool:
        now = self._time.now()
        idle_time = now - (self._additional_time + self._last_update)
        return idle_time <= self._life_time

    def _new_session(self):
        self._profile_id = self._profile_source.get_profile()
        self._actual_session = self._session_repo.new_session(
            instruction=self._instruction,
            profile_id=self._profile_id,
        )
        self._logger.info("created new session with id: %s", self._actual_session)
