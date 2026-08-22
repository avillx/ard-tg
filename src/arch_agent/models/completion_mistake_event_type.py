from enum import Enum


class CompletionMistakeEventType(str, Enum):
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
