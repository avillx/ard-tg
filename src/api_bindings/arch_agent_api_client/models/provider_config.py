from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_config_models import ProviderConfigModels


T = TypeVar("T", bound="ProviderConfig")


@_attrs_define
class ProviderConfig:
    """Configuration for an API provider (OpenAI-compatible endpoint).

    Example:
        {'name': 'openai', 'base_url': 'https://api.openai.com/v1', 'api_type': 'openai', 'key_ref': 'openai_key',
            'models': {'gpt-4': {'temperature': 0.7}}}

    Attributes:
        name (str): Provider name.
        base_url (str): Base URL for the API endpoint.
        api_type (str): API type (e.g. `openai`).
        key_ref (str | Unset): Reference to the API key in secrets.
        models (ProviderConfigModels | Unset): Model configurations keyed by model name.
    """

    name: str
    base_url: str
    api_type: str
    key_ref: str | Unset = UNSET
    models: ProviderConfigModels | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        base_url = self.base_url

        api_type = self.api_type

        key_ref = self.key_ref

        models: dict[str, Any] | Unset = UNSET
        if not isinstance(self.models, Unset):
            models = self.models.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "base_url": base_url,
                "api_type": api_type,
            }
        )
        if key_ref is not UNSET:
            field_dict["key_ref"] = key_ref
        if models is not UNSET:
            field_dict["models"] = models

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_config_models import ProviderConfigModels

        d = dict(src_dict)
        name = d.pop("name")

        base_url = d.pop("base_url")

        api_type = d.pop("api_type")

        key_ref = d.pop("key_ref", UNSET)

        _models = d.pop("models", UNSET)
        models: ProviderConfigModels | Unset
        if isinstance(_models, Unset):
            models = UNSET
        else:
            models = ProviderConfigModels.from_dict(_models)

        provider_config = cls(
            name=name,
            base_url=base_url,
            api_type=api_type,
            key_ref=key_ref,
            models=models,
        )

        provider_config.additional_properties = d
        return provider_config

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
