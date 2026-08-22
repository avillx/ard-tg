from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .tool_result_event_type import ToolResultEventType

if TYPE_CHECKING:
    from .content_part import ContentPart


T = TypeVar("T", bound="ToolResultEvent")


@_attrs_define
class ToolResultEvent:
    """Result of a tool call. Emitted with type `tool_result`.

    Example:
        {'type': 'tool_result', 'id': 'call_abc', 'result': [{'text': 'File contents'}]}

    Attributes:
        type_ (ToolResultEventType):
        id (str): Tool call ID.
        result (list[ContentPart]): Tool call result content.
    """

    type_: ToolResultEventType
    id: str
    result: list[ContentPart]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        id = self.id

        result = []
        for result_item_data in self.result:
            result_item = result_item_data.to_dict()
            result.append(result_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "id": id,
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .content_part import ContentPart

        d = dict(src_dict)
        type_ = ToolResultEventType(d.pop("type"))

        id = d.pop("id")

        result = []
        _result = d.pop("result")
        for result_item_data in _result:
            result_item = ContentPart.from_dict(result_item_data)

            result.append(result_item)

        tool_result_event = cls(
            type_=type_,
            id=id,
            result=result,
        )

        tool_result_event.additional_properties = d
        return tool_result_event

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
