from enum import Enum


class MessageDTORole(str, Enum):
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
