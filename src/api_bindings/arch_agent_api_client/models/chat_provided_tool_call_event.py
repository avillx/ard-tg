from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_provided_tool_call_event_type import ChatProvidedToolCallEventType

if TYPE_CHECKING:
    from ..models.chat_provided_tool_call_payload import ChatProvidedToolCallPayload


T = TypeVar("T", bound="ChatProvidedToolCallEvent")


@_attrs_define
class ChatProvidedToolCallEvent:
    """
    Attributes:
        type_ (ChatProvidedToolCallEventType):
        payload (ChatProvidedToolCallPayload): Payload of a provided tool call event in the chat stream. Example:
            {'tool': 'my_tool', 'args': {}, 'result_id': 'fg1ds12sg3d3f3fg342234d', 'agent_id': 'agent_1', 'session_id':
            'sess_1'}.
    """

    type_: ChatProvidedToolCallEventType
    payload: ChatProvidedToolCallPayload
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
        from ..models.chat_provided_tool_call_payload import ChatProvidedToolCallPayload

        d = dict(src_dict)
        type_ = ChatProvidedToolCallEventType(d.pop("type"))

        payload = ChatProvidedToolCallPayload.from_dict(d.pop("payload"))

        chat_provided_tool_call_event = cls(
            type_=type_,
            payload=payload,
        )

        chat_provided_tool_call_event.additional_properties = d
        return chat_provided_tool_call_event

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
