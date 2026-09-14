from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tool_call_args import ToolCallArgs


T = TypeVar("T", bound="ToolCall")


@_attrs_define
class ToolCall:
    """A tool call made by the model during a chat completion.

    Example:
        {'id': 'call_abc123', 'tool': 'read_file', 'args': {'path': '/data/report.txt'}}

    Attributes:
        id (str): Tool call ID assigned by the model provider.
        tool (str): Tool name.
        args (ToolCallArgs): Tool arguments. The actual schema is determined by the tool definition.
    """

    id: str
    tool: str
    args: ToolCallArgs
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tool = self.tool

        args = self.args.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tool": tool,
                "args": args,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_call_args import ToolCallArgs

        d = dict(src_dict)
        id = d.pop("id")

        tool = d.pop("tool")

        args = ToolCallArgs.from_dict(d.pop("args"))

        tool_call = cls(
            id=id,
            tool=tool,
            args=args,
        )

        tool_call.additional_properties = d
        return tool_call

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
