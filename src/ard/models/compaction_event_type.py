from enum import StrEnum


class CompactionEventType(StrEnum):
    COMPACTION = "compaction"

    def __str__(self) -> str:
        return str(self.value)
