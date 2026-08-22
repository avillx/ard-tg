from enum import Enum


class CompletionDTOType(str, Enum):
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
