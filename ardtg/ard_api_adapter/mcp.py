from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.mcp import list_mcp_servers
from ardtg.domain.mcp import MCPRepo

if TYPE_CHECKING:
    import logging

    from ardtg.ard_api import Client


class AgentAPIMCPListAdapter(MCPRepo):
    _logger: logging.Logger
    _agent_client: Client

    def __init__(
        self,
        client: Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    @override
    def mcp_list(self) -> list[str]:
        """Return the MCP servers known to the agent."""
        self._logger.info("MCP servers requested")

        mcp_servers = list_mcp_servers.sync(client=self._agent_client)
        if mcp_servers is None:
            return []

        result: list[str] = []
        for mcp_id in mcp_servers.additional_properties:
            result.append(mcp_id)

        return result
