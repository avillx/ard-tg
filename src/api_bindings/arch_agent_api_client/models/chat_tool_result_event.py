from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_tool_result_event_type import ChatToolResultEventType

if TYPE_CHECKING:
    from ..models.chat_tool_result_payload import ChatToolResultPayload


T = TypeVar("T", bound="ChatToolResultEvent")


@_attrs_define
class ChatToolResultEvent:
    """
    Attributes:
        type_ (ChatToolResultEventType):
        payload (ChatToolResultPayload): Payload of a tool result event in the chat stream. Example: {'id': 'call_abc',
            'result': [{'text': 'File contents'}]}.
    """

    type_: ChatToolResultEventType
    payload: ChatToolResultPayload
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "payload": payload,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_tool_result_payload import ChatToolResultPayload

        d = dict(src_dict)
        type_ = ChatToolResultEventType(d.pop("type"))

        payload = ChatToolResultPayload.from_dict(d.pop("payload"))

        chat_tool_result_event = cls(
            type_=type_,
            payload=payload,
        )

        chat_tool_result_event.additional_properties = d
        return chat_tool_result_event

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
