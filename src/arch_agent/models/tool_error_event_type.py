from enum import Enum


class ToolErrorEventType(str, Enum):
    COMPLETE_MISTAKE = "complete_mistake"

    def __str__(self) -> str:
        return str(self.value)
