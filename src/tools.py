from abc import ABC, abstractmethod

import api_bindings.arch_agent_api_client.models as models


class AgentTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def schema(self) -> dict[str,any]:
        pass

    @abstractmethod
    def execute(self,ags : dict[str,any]) -> str:
        pass

def create_provided_tool_server(tools : list[AgentTool]) -> models.ProvidedToolServer:

    provided_tools : list[models.ProvidedTool] = []

    for t in tools:
        provided_tools.append(
            models.ProvidedTool(
                name=t.name(),
                description=t.description(),
                schema=models.ProvidedToolSchema.from_dict(t.schema()),
            )
        )

    return models.ProvidedToolServer(tools=provided_tools)
