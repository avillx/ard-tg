from enum import Enum


class ChatErrorEventType(str, Enum):
    ERROR = "error"

    def __str__(self) -> str:
        return str(self.value)
