from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSessionBody")


@_attrs_define
class CreateSessionBody:
    """
    Attributes:
        profile_id (str | Unset): Profile the session belongs to.
        instruction (str | Unset): Optional initial instruction stored in session extras.
    """

    profile_id: str | Unset = UNSET
    instruction: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        instruction = self.instruction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if instruction is not UNSET:
            field_dict["instruction"] = instruction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        profile_id = d.pop("profile_id", UNSET)

        instruction = d.pop("instruction", UNSET)

        create_session_body = cls(
            profile_id=profile_id,
            instruction=instruction,
        )

        create_session_body.additional_properties = d
        return create_session_body

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
