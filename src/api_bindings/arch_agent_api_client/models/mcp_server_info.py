from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_info import ToolInfo


T = TypeVar("T", bound="MCPServerInfo")


@_attrs_define
class MCPServerInfo:
    """A connected MCP server with its transport type, name, and tools.

    Example:
        {'transport': 'http', 'name': 'my-mcp-server', 'tools': [{'name': 'fetch', 'description': 'Fetch a URL'}]}

    Attributes:
        transport (str | Unset): Transport type. `http` for remote servers, `process` for local spawned processes.
            Example: http.
        name (str | Unset): MCP server ID/name.
        tools (list[ToolInfo] | Unset):
    """

    transport: str | Unset = UNSET
    name: str | Unset = UNSET
    tools: list[ToolInfo] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transport = self.transport

        name = self.name

        tools: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = []
            for tools_item_data in self.tools:
                tools_item = tools_item_data.to_dict()
                tools.append(tools_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if transport is not UNSET:
            field_dict["transport"] = transport
        if name is not UNSET:
            field_dict["name"] = name
        if tools is not UNSET:
            field_dict["tools"] = tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_info import ToolInfo

        d = dict(src_dict)
        transport = d.pop("transport", UNSET)

        name = d.pop("name", UNSET)

        _tools = d.pop("tools", UNSET)
        tools: list[ToolInfo] | Unset = UNSET
        if _tools is not UNSET:
            tools = []
            for tools_item_data in _tools:
                tools_item = ToolInfo.from_dict(tools_item_data)

                tools.append(tools_item)

        mcp_server_info = cls(
            transport=transport,
            name=name,
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
