from abc import ABC, abstractmethod
from typing import Any

import ard.models as models

ToolArgs = dict[str, Any] # pyright: ignore[reportExplicitAny]
ToolSchema = dict[str, Any] # pyright: ignore[reportExplicitAny]

class Tool(ABC):
    _name: str
    _desctiption: str
    _schema: ToolSchema

    def __init__(
        self,
        name: str,
        description: str,
        schema: ToolSchema
    ):
        self._name = name
        self._desctiption = description
        self._schema = schema


    def name(self) -> str:
        return self._name


    def description(self) -> str:
        return self._desctiption


    def schema(self) -> ToolSchema:
        return self._schema


    @abstractmethod
    def execute(self, args: ToolArgs) -> str:
        pass


def create_provided_tool_server(tools: list[Tool]) -> models.ProvidedToolServer:

    provided_tools: list[models.ProvidedTool] = []

    for t in tools:
        provided_tools.append(
            models.ProvidedTool(
                name=t.name(),
                description=t.description(),
                schema=models.ProvidedToolSchema.from_dict(t.schema()),
            )
        )

    return models.ProvidedToolServer(tools=provided_tools)
