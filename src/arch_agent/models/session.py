from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .message_dto import MessageDTO
    from .session_extras import SessionExtras


T = TypeVar("T", bound="Session")


@_attrs_define
class Session:
    """A session represents a conversation with an agent.
    It contains the message history, token usage, and timestamps.

        Example:
            {'session_id': 'sess_01J...', 'messages': [{'role': 'user', 'content': [{'text': 'Read the report'}]}],
                'input_tokens': 150, 'output_tokens': 42, 'created_at': '2025-01-01T00:00:00Z', 'updated_at':
                '2025-01-01T00:05:00Z'}

        Attributes:
            session_id (str | Unset):
            messages (list[MessageDTO] | Unset):
            input_tokens (int | Unset):
            output_tokens (int | Unset):
            created_at (datetime.datetime | Unset):
            updated_at (datetime.datetime | Unset):
            extras (SessionExtras | Unset):
    """

    session_id: str | Unset = UNSET
    messages: list[MessageDTO] | Unset = UNSET
    input_tokens: int | Unset = UNSET
    output_tokens: int | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    extras: SessionExtras | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        messages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        input_tokens = self.input_tokens

        output_tokens = self.output_tokens

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        extras: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extras, Unset):
            extras = self.extras.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if messages is not UNSET:
            field_dict["messages"] = messages
        if input_tokens is not UNSET:
            field_dict["input_tokens"] = input_tokens
        if output_tokens is not UNSET:
            field_dict["output_tokens"] = output_tokens
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if extras is not UNSET:
            field_dict["extras"] = extras

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .message_dto import MessageDTO
        from .session_extras import SessionExtras

        d = dict(src_dict)
        session_id = d.pop("session_id", UNSET)

        _messages = d.pop("messages", UNSET)
        messages: list[MessageDTO] | Unset = UNSET
        if _messages is not UNSET:
            messages = []
            for messages_item_data in _messages:
                messages_item = MessageDTO.from_dict(messages_item_data)

                messages.append(messages_item)

        input_tokens = d.pop("input_tokens", UNSET)

        output_tokens = d.pop("output_tokens", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = datetime.datetime.fromisoformat(_updated_at)

        _extras = d.pop("extras", UNSET)
        extras: SessionExtras | Unset
        if isinstance(_extras, Unset):
            extras = UNSET
        else:
            extras = SessionExtras.from_dict(_extras)

        session = cls(
            session_id=session_id,
            messages=messages,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            created_at=created_at,
            updated_at=updated_at,
            extras=extras,
        )

        session.additional_properties = d
        return session

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
