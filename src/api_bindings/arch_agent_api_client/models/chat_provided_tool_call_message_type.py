from enum import Enum


class ChatProvidedToolCallMessageType(str, Enum):
    PROVIDED_TOOLCALL = "provided_toolcall"

    def __str__(self) -> str:
        return str(self.value)
