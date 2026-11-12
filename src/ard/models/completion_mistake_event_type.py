from enum import Enum


class CompletionMistakeEventType(str, Enum):
    COMPLETE_MISTAKE = "complete_mistake"

    def __str__(self) -> str:
        return str(self.value)
