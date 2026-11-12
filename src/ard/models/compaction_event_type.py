from enum import Enum


class CompactionEventType(str, Enum):
    COMPACTION = "compaction"

    def __str__(self) -> str:
        return str(self.value)
