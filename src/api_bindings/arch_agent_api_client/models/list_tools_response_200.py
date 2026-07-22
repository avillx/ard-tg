from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_server_info import ToolServerInfo


T = TypeVar("T", bound="ListToolsResponse200")


@_attrs_define
class ListToolsResponse200:
    """
    Attributes:
        tool_servers (list[ToolServerInfo] | Unset):
    """

    tool_servers: list[ToolServerInfo] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool_servers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tool_servers, Unset):
            tool_servers = []
            for tool_servers_item_data in self.tool_servers:
                tool_servers_item = tool_servers_item_data.to_dict()
                tool_servers.append(tool_servers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tool_servers is not UNSET:
            field_dict["tool_servers"] = tool_servers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_server_info import ToolServerInfo

        d = dict(src_dict)
        _tool_servers = d.pop("tool_servers", UNSET)
        tool_servers: list[ToolServerInfo] | Unset = UNSET
        if _tool_servers is not UNSET:
            tool_servers = []
            for tool_servers_item_data in _tool_servers:
                tool_servers_item = ToolServerInfo.from_dict(tool_servers_item_data)

                tool_servers.append(tool_servers_item)

        list_tools_response_200 = cls(
            tool_servers=tool_servers,
        )

        list_tools_response_200.additional_properties = d
        return list_tools_response_200

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
