from enum import Enum


class ChatCompactionEventType(str, Enum):
    COMPACTION = "compaction"

    def __str__(self) -> str:
        return str(self.value)
