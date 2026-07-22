from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_completion_message_type import ChatCompletionMessageType

if TYPE_CHECKING:
    from ..models.chat_completion_payload import ChatCompletionPayload


T = TypeVar("T", bound="ChatCompletionMessage")


@_attrs_define
class ChatCompletionMessage:
    """
    Attributes:
        type_ (ChatCompletionMessageType):
        payload (ChatCompletionPayload): Payload of a completion event in the chat stream. Example: {'done': False,
            'completion': 'Hello!', 'tool_calls': []}.
    """

    type_: ChatCompletionMessageType
    payload: ChatCompletionPayload
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
        from ..models.chat_completion_payload import ChatCompletionPayload

        d = dict(src_dict)
        type_ = ChatCompletionMessageType(d.pop("type"))

        payload = ChatCompletionPayload.from_dict(d.pop("payload"))

        chat_completion_message = cls(
            type_=type_,
            payload=payload,
        )

        chat_completion_message.additional_properties = d
        return chat_completion_message

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
