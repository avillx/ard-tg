from enum import StrEnum


class ToolResultEventType(StrEnum):
    TOOL_RESULT = "tool_result"

    def __str__(self) -> str:
        return str(self.value)
