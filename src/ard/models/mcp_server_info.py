from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.server_gateway_config import ServerGatewayConfig
    from ..models.tool_repr import ToolRepr


T = TypeVar("T", bound="MCPServerInfo")


@_attrs_define
class MCPServerInfo:
    """A connected MCP server with its config and tools.

    Attributes:
        config (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be provided.
            If neither or both are provided, the request is rejected with 400.
        tools (ToolRepr): A mapping of tool name to its description.
    """

    config: ServerGatewayConfig
    tools: ToolRepr
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config = self.config.to_dict()

        tools = self.tools.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "tools": tools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_gateway_config import ServerGatewayConfig
        from ..models.tool_repr import ToolRepr

        d = dict(src_dict)
        config = ServerGatewayConfig.from_dict(d.pop("config"))

        tools = ToolRepr.from_dict(d.pop("tools"))

        mcp_server_info = cls(
            config=config,
            tools=tools,
        )

        mcp_server_info.additional_properties = d
        return mcp_server_info

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
