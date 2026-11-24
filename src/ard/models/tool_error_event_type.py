from enum import StrEnum


class ToolErrorEventType(StrEnum):
    TOOL_ERROR = "tool_error"

    def __str__(self) -> str:
        return str(self.value)
