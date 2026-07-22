from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MCPConnectResponse")


@_attrs_define
class MCPConnectResponse:
    """Response from a successful MCP server connection.

    Example:
        {'msg': 'success', 'created_id': 'mcp_server_1'}

    Attributes:
        msg (str | Unset):  Example: success.
        created_id (str | Unset):
    """

    msg: str | Unset = UNSET
    created_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        msg = self.msg

        created_id = self.created_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if msg is not UNSET:
            field_dict["msg"] = msg
        if created_id is not UNSET:
            field_dict["created_id"] = created_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        msg = d.pop("msg", UNSET)

        created_id = d.pop("created_id", UNSET)

        mcp_connect_response = cls(
            msg=msg,
            created_id=created_id,
        )

        mcp_connect_response.additional_properties = d
        return mcp_connect_response

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
