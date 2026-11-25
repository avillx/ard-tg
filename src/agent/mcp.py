lazy import logging

import ard.api.mcp.list_mcp_servers as list_mcp_servers
import ard.client as agent_client
import ard.models as models


class McpListService:
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    def mcp_list(self) -> dict[str, models.MCPServerInfo]:
        """Return the MCP servers known to the agent."""
        self._logger.info("MCP servers requested")

        mcp_servers = list_mcp_servers.sync(client=self._agent_client)
        if mcp_servers is None:
            return {}

        return mcp_servers.to_dict()
