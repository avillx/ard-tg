from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .tool_error_event_type import ToolErrorEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .tool_error_event_args import ToolErrorEventArgs


T = TypeVar("T", bound="ToolErrorEvent")


@_attrs_define
class ToolErrorEvent:
    """A tool execution error. Emitted with type `complete_mistake`.

    Example:
        {'type': 'complete_mistake', 'cause': 'permission denied', 'tool_name': 'read_file', 'args': {'path':
            '/etc/shadow'}}

    Attributes:
        type_ (ToolErrorEventType):
        cause (str): Human-readable error message.
        tool_name (str): Name of the tool that failed.
        args (ToolErrorEventArgs | Unset): Arguments passed to the failed tool call.
    """

    type_: ToolErrorEventType
    cause: str
    tool_name: str
    args: ToolErrorEventArgs | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        cause = self.cause

        tool_name = self.tool_name

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "cause": cause,
                "tool_name": tool_name,
            }
        )
        if args is not UNSET:
            field_dict["args"] = args

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .tool_error_event_args import ToolErrorEventArgs

        d = dict(src_dict)
        type_ = ToolErrorEventType(d.pop("type"))

        cause = d.pop("cause")

        tool_name = d.pop("tool_name")

        _args = d.pop("args", UNSET)
        args: ToolErrorEventArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = ToolErrorEventArgs.from_dict(_args)

        tool_error_event = cls(
            type_=type_,
            cause=cause,
            tool_name=tool_name,
            args=args,
        )

        tool_error_event.additional_properties = d
        return tool_error_event

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
