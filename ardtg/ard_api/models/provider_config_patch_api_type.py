from enum import StrEnum


class ProviderConfigPatchApiType(StrEnum):
    OPENAI = "openai"

    def __str__(self) -> str:
        return str(self.value)
