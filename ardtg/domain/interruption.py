from abc import ABC, abstractmethod


class Interruptor(ABC):
    @abstractmethod
    def interrupt(self, session_id: str) -> None:
        pass
