from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_header_extras import SessionHeaderExtras


T = TypeVar("T", bound="SessionHeader")


@_attrs_define
class SessionHeader:
    """Metadata for a single session. The `error` field is only present for
    broken (unreadable) session headers.

        Attributes:
            session_id (str):
            input_tokens (int):
            output_tokens (int):
            created_at (datetime.datetime):
            updated_at (datetime.datetime):
            extras (SessionHeaderExtras | Unset):
            error (str | Unset): Present only when the session header is broken.
    """

    session_id: str
    input_tokens: int
    output_tokens: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    extras: SessionHeaderExtras | Unset = UNSET
    error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        input_tokens = self.input_tokens

        output_tokens = self.output_tokens

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        extras: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extras, Unset):
            extras = self.extras.to_dict()

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session_id": session_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if extras is not UNSET:
            field_dict["extras"] = extras
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_header_extras import SessionHeaderExtras

        d = dict(src_dict)
        session_id = d.pop("session_id")

        input_tokens = d.pop("input_tokens")

        output_tokens = d.pop("output_tokens")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        _extras = d.pop("extras", UNSET)
        extras: SessionHeaderExtras | Unset
        if isinstance(_extras, Unset):
            extras = UNSET
        else:
            extras = SessionHeaderExtras.from_dict(_extras)

        error = d.pop("error", UNSET)

        session_header = cls(
            session_id=session_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            created_at=created_at,
            updated_at=updated_at,
            extras=extras,
            error=error,
        )

        session_header.additional_properties = d
        return session_header

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
