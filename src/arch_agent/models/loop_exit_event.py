from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .loop_exit_event_type import LoopExitEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="LoopExitEvent")


@_attrs_define
class LoopExitEvent:
    """The agent runtime stopped due to an error. Emitted with type `tool_result`.

    Example:
        {'type': 'tool_result', 'cause': 'maximum iterations exceeded'}

    Attributes:
        type_ (LoopExitEventType):
        cause (str | Unset): Human-readable error message explaining why the loop exited.
    """

    type_: LoopExitEventType
    cause: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        cause = self.cause

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if cause is not UNSET:
            field_dict["cause"] = cause

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = LoopExitEventType(d.pop("type"))

        cause = d.pop("cause", UNSET)

        loop_exit_event = cls(
            type_=type_,
            cause=cause,
        )

        loop_exit_event.additional_properties = d
        return loop_exit_event

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
