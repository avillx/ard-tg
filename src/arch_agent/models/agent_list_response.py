from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .agent_config import AgentConfig


T = TypeVar("T", bound="AgentListResponse")


@_attrs_define
class AgentListResponse:
    """List of all configured agents.

    Example:
        {'agents': [{'model': 'gpt-4', 'memory': True, 'description': 'General assistant'}]}

    Attributes:
        agents (list[AgentConfig] | Unset):
    """

    agents: list[AgentConfig] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agents: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.agents, Unset):
            agents = []
            for agents_item_data in self.agents:
                agents_item = agents_item_data.to_dict()
                agents.append(agents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agents is not UNSET:
            field_dict["agents"] = agents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .agent_config import AgentConfig

        d = dict(src_dict)
        _agents = d.pop("agents", UNSET)
        agents: list[AgentConfig] | Unset = UNSET
        if _agents is not UNSET:
            agents = []
            for agents_item_data in _agents:
                agents_item = AgentConfig.from_dict(agents_item_data)

                agents.append(agents_item)

        agent_list_response = cls(
            agents=agents,
        )

        agent_list_response.additional_properties = d
        return agent_list_response

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
