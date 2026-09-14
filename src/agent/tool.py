from abc import ABC, abstractmethod
from typing import Any

import arch_agent.models as models


class AgentTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def schema(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, args: dict[str, Any]) -> str:
        pass


def create_provided_tool_server(tools: list[AgentTool]) -> models.ProvidedToolServer:

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


class SafeTool(AgentTool):
    _name: str
    _desctiption: str
    _schema: dict[str, Any]

    def __init__(
        self,
        name: str,
        description: str,
        schema: dict[str, Any],
    ):
        self._name = name
        self._desctiption = description
        self._schema = schema

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._desctiption

    def schema(self) -> dict[str, Any]:
        return self._schema

    def execute(self, args: dict[str, Any]) -> str:
        try:
            return self._execute(args)
        except Exception as e:
            return f"error: {e}"

    @abstractmethod
    def _execute(self, args: dict[str, Any]) -> str:
        pass
