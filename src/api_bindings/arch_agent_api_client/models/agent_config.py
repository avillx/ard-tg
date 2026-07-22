from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentConfig")


@_attrs_define
class AgentConfig:
    """Configuration for an agent. At minimum, a model must be specified.

    Example:
        {'model': 'gpt-4', 'memory': True, 'description': 'General assistant', 'tool_servers': ['filesystem', 'search']}

    Attributes:
        model (str | Unset): Model identifier (e.g. `gpt-4`, `claude-3-opus`).
        memory (bool | Unset): Whether memory is enabled.
        description (str | Unset):
        tool_servers (list[str] | Unset): Allowed tool server names.
        system_prompt (str | Unset): Custom system prompt override.
    """

    model: str | Unset = UNSET
    memory: bool | Unset = UNSET
    description: str | Unset = UNSET
    tool_servers: list[str] | Unset = UNSET
    system_prompt: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model = self.model

        memory = self.memory

        description = self.description

        tool_servers: list[str] | Unset = UNSET
        if not isinstance(self.tool_servers, Unset):
            tool_servers = self.tool_servers

        system_prompt = self.system_prompt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model is not UNSET:
            field_dict["model"] = model
        if memory is not UNSET:
            field_dict["memory"] = memory
        if description is not UNSET:
            field_dict["description"] = description
        if tool_servers is not UNSET:
            field_dict["tool_servers"] = tool_servers
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model = d.pop("model", UNSET)

        memory = d.pop("memory", UNSET)

        description = d.pop("description", UNSET)

        tool_servers = cast(list[str], d.pop("tool_servers", UNSET))

        system_prompt = d.pop("system_prompt", UNSET)

        agent_config = cls(
            model=model,
            memory=memory,
            description=description,
            tool_servers=tool_servers,
            system_prompt=system_prompt,
        )

        agent_config.additional_properties = d
        return agent_config

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
