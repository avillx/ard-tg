from enum import StrEnum


class CompletionEventType(StrEnum):
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
