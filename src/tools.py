import api_bindings.arch_agent_api_client.models as models
import api_bindings.arch_agent_api_client.client as agent_client
import api_bindings.arch_agent_api_client.api.tool_results.resolve_tool_call as tool_result
from abc import ABC, abstractmethod
from typing import Callable
import asyncio

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