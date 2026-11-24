from enum import StrEnum


class ProviderConfigApiType(StrEnum):
    OPENAI = "openai"

    def __str__(self) -> str:
        return str(self.value)
