from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MemoryDetail")


@_attrs_define
class MemoryDetail:
    """Full content of a named memory record.

    Example:
        {'agent': 'agent_main', 'memory_name': 'week_25', 'content': 'The agent processed 15 tasks...'}

    Attributes:
        agent (str | Unset):
        memory_name (str | Unset):
        content (str | Unset):
    """

    agent: str | Unset = UNSET
    memory_name: str | Unset = UNSET
    content: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent

        memory_name = self.memory_name

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agent is not UNSET:
            field_dict["agent"] = agent
        if memory_name is not UNSET:
            field_dict["memory_name"] = memory_name
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent = d.pop("agent", UNSET)

        memory_name = d.pop("memory_name", UNSET)

        content = d.pop("content", UNSET)

        memory_detail = cls(
            agent=agent,
            memory_name=memory_name,
            content=content,
        )

        memory_detail.additional_properties = d
        return memory_detail

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
