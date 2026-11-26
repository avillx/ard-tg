from abc import ABC, abstractmethod


class MCPRepo(ABC):
    @abstractmethod
    def mcp_list(self) -> list[str]:
        pass
