from enum import Enum


class ChatProvidedToolCallEventType(str, Enum):
    PROVIDED_TOOLCALL = "provided_toolcall"

    def __str__(self) -> str:
        return str(self.value)
