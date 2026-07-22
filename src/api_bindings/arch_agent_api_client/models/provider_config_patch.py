from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProviderConfigPatch")


@_attrs_define
class ProviderConfigPatch:
    """Partial update for a provider. Only supplied fields are updated. Fields set to `null` are ignored.

    Attributes:
        name (None | str | Unset):
        base_url (None | str | Unset):
        key_ref (None | str | Unset):
        api_type (None | str | Unset):
    """

    name: None | str | Unset = UNSET
    base_url: None | str | Unset = UNSET
    key_ref: None | str | Unset = UNSET
    api_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        key_ref: None | str | Unset
        if isinstance(self.key_ref, Unset):
            key_ref = UNSET
        else:
            key_ref = self.key_ref

        api_type: None | str | Unset
        if isinstance(self.api_type, Unset):
            api_type = UNSET
        else:
            api_type = self.api_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if key_ref is not UNSET:
            field_dict["key_ref"] = key_ref
        if api_type is not UNSET:
            field_dict["api_type"] = api_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_key_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        key_ref = _parse_key_ref(d.pop("key_ref", UNSET))

        def _parse_api_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_type = _parse_api_type(d.pop("api_type", UNSET))

        provider_config_patch = cls(
            name=name,
            base_url=base_url,
            key_ref=key_ref,
            api_type=api_type,
        )

        provider_config_patch.additional_properties = d
        return provider_config_patch

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
