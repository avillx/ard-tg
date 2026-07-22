from enum import Enum


class ChatCompletionMessageType(str, Enum):
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
