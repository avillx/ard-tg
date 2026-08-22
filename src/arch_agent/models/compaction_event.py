from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .compaction_event_type import CompactionEventType

T = TypeVar("T", bound="CompactionEvent")


@_attrs_define
class CompactionEvent:
    """Session context was compacted. Emitted with type `compaction`.

    Example:
        {'type': 'compaction', 'message': 'compaction has been proceed', 'result': 'summary text'}

    Attributes:
        type_ (CompactionEventType):
        message (str): Human-readable compaction status message.
        result (str): Compaction summary text.
    """

    type_: CompactionEventType
    message: str
    result: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        message = self.message

        result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "message": message,
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CompactionEventType(d.pop("type"))

        message = d.pop("message")

        result = d.pop("result")

        compaction_event = cls(
            type_=type_,
            message=message,
            result=result,
        )

        compaction_event.additional_properties = d
        return compaction_event

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
