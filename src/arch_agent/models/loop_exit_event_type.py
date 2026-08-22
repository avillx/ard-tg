from enum import Enum


class LoopExitEventType(str, Enum):
    TOOL_RESULT = "tool_result"

    def __str__(self) -> str:
        return str(self.value)
