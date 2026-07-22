from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.memory_list_response_memory_records_item import MemoryListResponseMemoryRecordsItem


T = TypeVar("T", bound="MemoryListResponse")


@_attrs_define
class MemoryListResponse:
    """Memory index for an agent.

    Example:
        {'agent': 'agent_main', 'memory_records': [{'name': 'week_25', 'description': 'Activity summary for week 25'}]}

    Attributes:
        agent (str | Unset):
        memory_records (list[MemoryListResponseMemoryRecordsItem] | Unset):
    """

    agent: str | Unset = UNSET
    memory_records: list[MemoryListResponseMemoryRecordsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent

        memory_records: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.memory_records, Unset):
            memory_records = []
            for memory_records_item_data in self.memory_records:
                memory_records_item = memory_records_item_data.to_dict()
                memory_records.append(memory_records_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agent is not UNSET:
            field_dict["agent"] = agent
        if memory_records is not UNSET:
            field_dict["memory_records"] = memory_records

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.memory_list_response_memory_records_item import MemoryListResponseMemoryRecordsItem

        d = dict(src_dict)
        agent = d.pop("agent", UNSET)

        _memory_records = d.pop("memory_records", UNSET)
        memory_records: list[MemoryListResponseMemoryRecordsItem] | Unset = UNSET
        if _memory_records is not UNSET:
            memory_records = []
            for memory_records_item_data in _memory_records:
                memory_records_item = MemoryListResponseMemoryRecordsItem.from_dict(memory_records_item_data)

                memory_records.append(memory_records_item)

        memory_list_response = cls(
            agent=agent,
            memory_records=memory_records,
        )

        memory_list_response.additional_properties = d
        return memory_list_response

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
