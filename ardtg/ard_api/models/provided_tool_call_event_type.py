from enum import StrEnum


class ProvidedToolCallEventType(StrEnum):
    PROVIDED_TOOLCALL = "provided_toolcall"

    def __str__(self) -> str:
        return str(self.value)
