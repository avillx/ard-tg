from enum import Enum


class LoopExitEventType(str, Enum):
    LOOP_EXIT = "loop_exit"

    def __str__(self) -> str:
        return str(self.value)
