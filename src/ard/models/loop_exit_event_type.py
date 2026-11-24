from enum import StrEnum


class LoopExitEventType(StrEnum):
    LOOP_EXIT = "loop_exit"

    def __str__(self) -> str:
        return str(self.value)
