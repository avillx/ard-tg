from abc import ABC, abstractmethod
from datetime import UTC, datetime

from attr import dataclass


@dataclass(frozen=True, slots=True)
class ActivityRecord:
    date: str
    content: str


class ActivityRepo(ABC):
    @abstractmethod
    def get_activity(self, from_: datetime, to: datetime | None = None) -> list[ActivityRecord]:
        pass


class TodayActivity:
    _repo: ActivityRepo

    def __init__(self, repo: ActivityRepo):
        self._repo = repo

    def get_activity(self) -> list[ActivityRecord]:
        today = datetime.now(UTC)
        return self._repo.get_activity(from_=today)
