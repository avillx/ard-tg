from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_error_event_type import ChatErrorEventType

if TYPE_CHECKING:
    from ..models.chat_error_payload import ChatErrorPayload


T = TypeVar("T", bound="ChatErrorEvent")


@_attrs_define
class ChatErrorEvent:
    """
    Attributes:
        type_ (ChatErrorEventType):
        payload (ChatErrorPayload): Payload of an error event in the chat stream. Example: {'cause': 'something went
            wrong', 'session': 'sess_1', 'agent': 'agent_1'}.
    """

    type_: ChatErrorEventType
    payload: ChatErrorPayload
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
        from ..models.chat_error_payload import ChatErrorPayload

        d = dict(src_dict)
        type_ = ChatErrorEventType(d.pop("type"))

        payload = ChatErrorPayload.from_dict(d.pop("payload"))

        chat_error_event = cls(
            type_=type_,
            payload=payload,
        )

        chat_error_event.additional_properties = d
        return chat_error_event

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
