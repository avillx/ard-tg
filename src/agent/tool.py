from abc import ABC, abstractmethod
from typing import Any, override

import ard.models as models


class AgentTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def schema(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def execute(self, args: dict[str, Any]) -> str:  # pyright: ignore[reportExplicitAny]
        pass


class SafeTool(AgentTool, ABC):
    _name: str
    _desctiption: str
    _schema: dict[str, Any]  # pyright: ignore[reportExplicitAny]

    def __init__(
        self,
        name: str,
        description: str,
        schema: dict[str, Any],  # pyright: ignore[reportExplicitAny]
    ):
        self._name = name
        self._desctiption = description
        self._schema = schema

    @override
    def name(self) -> str:
        return self._name

    @override
    def description(self) -> str:
        return self._desctiption

    @override
    def schema(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._schema

    @override
    def execute(self, args: dict[str, Any]) -> str:  # pyright: ignore[reportExplicitAny]
        try:
            return self._execute(args)
        except Exception as e:  # noqa: BLE001 - tool code is arbitrary
            return f"error: {e}"

    @abstractmethod
    def _execute(self, args: dict[str, Any]) -> str:  # pyright: ignore[reportExplicitAny]
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
