from enum import Enum


class ProviderConfigApiType(str, Enum):
    OPENAI = "openai"

    def __str__(self) -> str:
        return str(self.value)
