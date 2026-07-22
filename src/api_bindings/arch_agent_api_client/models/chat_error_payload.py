from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatErrorPayload")


@_attrs_define
class ChatErrorPayload:
    """Payload of an error event in the chat stream.

    Example:
        {'cause': 'something went wrong', 'session': 'sess_1', 'agent': 'agent_1'}

    Attributes:
        cause (str | Unset): Human-readable error message.
        session (str | Unset): Session identifier.
        agent (str | Unset): Agent identifier.
    """

    cause: str | Unset = UNSET
    session: str | Unset = UNSET
    agent: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cause = self.cause

        session = self.session

        agent = self.agent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cause is not UNSET:
            field_dict["cause"] = cause
        if session is not UNSET:
            field_dict["session"] = session
        if agent is not UNSET:
            field_dict["agent"] = agent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cause = d.pop("cause", UNSET)

        session = d.pop("session", UNSET)

        agent = d.pop("agent", UNSET)

        chat_error_payload = cls(
            cause=cause,
            session=session,
            agent=agent,
        )

        chat_error_payload.additional_properties = d
        return chat_error_payload

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
