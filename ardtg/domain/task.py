from abc import ABC, abstractmethod

from attr import dataclass


@dataclass(frozen=True, slots=True)
class Task:
    name: str
    description: str
    recipients: list[str]
    schedule: str
    request: str
    active: bool
    oneshot: bool


class TasksListService(ABC):
    @abstractmethod
    def list(self) -> list[Task]:
        pass
