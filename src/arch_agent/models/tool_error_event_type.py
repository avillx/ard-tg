from enum import Enum


class ToolErrorEventType(str, Enum):
    TOOL_ERROR = "tool_error"

    def __str__(self) -> str:
        return str(self.value)
