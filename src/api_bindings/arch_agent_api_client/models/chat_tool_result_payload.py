from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.content_part import ContentPart


T = TypeVar("T", bound="ChatToolResultPayload")


@_attrs_define
class ChatToolResultPayload:
    """Payload of a tool result event in the chat stream.

    Example:
        {'id': 'call_abc', 'result': [{'text': 'File contents'}]}

    Attributes:
        id (str | Unset): Tool call ID.
        result (list[ContentPart] | Unset): Tool call result content.
    """

    id: str | Unset = UNSET
    result: list[ContentPart] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        result: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = []
            for result_item_data in self.result:
                result_item = result_item_data.to_dict()
                result.append(result_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.content_part import ContentPart

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _result = d.pop("result", UNSET)
        result: list[ContentPart] | Unset = UNSET
        if _result is not UNSET:
            result = []
            for result_item_data in _result:
                result_item = ContentPart.from_dict(result_item_data)

                result.append(result_item)

        chat_tool_result_payload = cls(
            id=id,
            result=result,
        )

        chat_tool_result_payload.additional_properties = d
        return chat_tool_result_payload

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
