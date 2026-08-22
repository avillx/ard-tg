from enum import Enum


class LoopExitEventType(str, Enum):
    TOOL_RESULT = "loop_exit"

    def __str__(self) -> str:
        return str(self.value)
