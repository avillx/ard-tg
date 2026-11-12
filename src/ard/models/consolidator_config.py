from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ConsolidatorConfig")


@_attrs_define
class ConsolidatorConfig:
    """Memory consolidation configuration.

    Example:
        {'Model': 'gpt-4', 'Enabled': True, 'Instruction': "Summarize the day's activity"}

    Attributes:
        model (str): Model name used for consolidation.
        enabled (bool): Whether automatic consolidation is enabled.
        instruction (str): Instruction passed to the consolidation agent.
    """

    model: str
    enabled: bool
    instruction: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model = self.model

        enabled = self.enabled

        instruction = self.instruction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Model": model,
                "Enabled": enabled,
                "Instruction": instruction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model = d.pop("Model")

        enabled = d.pop("Enabled")

        instruction = d.pop("Instruction")

        consolidator_config = cls(
            model=model,
            enabled=enabled,
            instruction=instruction,
        )

        consolidator_config.additional_properties = d
        return consolidator_config

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
