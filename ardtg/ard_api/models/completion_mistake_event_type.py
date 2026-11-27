from enum import StrEnum


class CompletionMistakeEventType(StrEnum):
    COMPLETE_MISTAKE = "complete_mistake"

    def __str__(self) -> str:
        return str(self.value)
