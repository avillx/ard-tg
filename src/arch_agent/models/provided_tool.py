from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .provided_tool_schema import ProvidedToolSchema


T = TypeVar("T", bound="ProvidedTool")


@_attrs_define
class ProvidedTool:
    """A single client-provided tool with optional JSON Schema for parameters.

    Example:
        {'name': 'my_custom_tool', 'description': 'A custom tool', 'schema': {'type': 'object', 'properties': {'input':
            {'type': 'string'}}}}

    Attributes:
        name (str):
        description (str):
        schema (ProvidedToolSchema | Unset): Optional JSON Schema for the tool's parameters.
    """

    name: str
    description: str
    schema: ProvidedToolSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .provided_tool_schema import ProvidedToolSchema

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        _schema = d.pop("schema", UNSET)
        schema: ProvidedToolSchema | Unset
        if isinstance(_schema, Unset):
            schema = UNSET
        else:
            schema = ProvidedToolSchema.from_dict(_schema)

        provided_tool = cls(
            name=name,
            description=description,
            schema=schema,
        )

        provided_tool.additional_properties = d
        return provided_tool

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
