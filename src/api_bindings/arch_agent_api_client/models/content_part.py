from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ContentPart")


@_attrs_define
class ContentPart:
    """A part of message content. At least one of `text` or `image_url` is present.

    Example:
        {'text': 'Hello, how are you?'}

    Attributes:
        text (str | Unset): Plain text content.
        image_url (str | Unset): Base64-encoded image data URL (e.g. `data:image/png;base64,...`).
            Supported formats: PNG, JPEG, WebP, GIF.
    """

    text: str | Unset = UNSET
    image_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        image_url = self.image_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if image_url is not UNSET:
            field_dict["image_url"] = image_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        text = d.pop("text", UNSET)

        image_url = d.pop("image_url", UNSET)

        content_part = cls(
            text=text,
            image_url=image_url,
        )

        content_part.additional_properties = d
        return content_part

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
