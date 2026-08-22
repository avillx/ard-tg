from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .provided_tool import ProvidedTool


T = TypeVar("T", bound="ProvidedToolServer")


@_attrs_define
class ProvidedToolServer:
    """Client-provided tool servers available for a single chat call.
    The client guarantees execution and returns results via the tool result endpoint.

        Example:
            {'tools': [{'name': 'my_custom_tool', 'description': 'A custom tool', 'schema': {'type': 'object', 'properties':
                {'input': {'type': 'string'}}}}], 'instruction': 'Use my_custom_tool when the user asks for custom data'}

        Attributes:
            tools (list[ProvidedTool]):
            instruction (str | Unset): Optional instruction for the agent about how to use these tools.
    """

    tools: list[ProvidedTool]
    instruction: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tools = []
        for tools_item_data in self.tools:
            tools_item = tools_item_data.to_dict()
            tools.append(tools_item)

        instruction = self.instruction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tools": tools,
            }
        )
        if instruction is not UNSET:
            field_dict["instruction"] = instruction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .provided_tool import ProvidedTool

        d = dict(src_dict)
        tools = []
        _tools = d.pop("tools")
        for tools_item_data in _tools:
            tools_item = ProvidedTool.from_dict(tools_item_data)

            tools.append(tools_item)

        instruction = d.pop("instruction", UNSET)

        provided_tool_server = cls(
            tools=tools,
            instruction=instruction,
        )

        provided_tool_server.additional_properties = d
        return provided_tool_server

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
