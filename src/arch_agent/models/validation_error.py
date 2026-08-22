from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .validation_error_problems import ValidationErrorProblems


T = TypeVar("T", bound="ValidationError")


@_attrs_define
class ValidationError:
    """Validation error response with per-field problems.

    Example:
        {'problems': {'schedule': 'invalid cron expression'}}

    Attributes:
        problems (ValidationErrorProblems | Unset): Map of field names to error messages.
    """

    problems: ValidationErrorProblems | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        problems: dict[str, Any] | Unset = UNSET
        if not isinstance(self.problems, Unset):
            problems = self.problems.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if problems is not UNSET:
            field_dict["problems"] = problems

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .validation_error_problems import ValidationErrorProblems

        d = dict(src_dict)
        _problems = d.pop("problems", UNSET)
        problems: ValidationErrorProblems | Unset
        if isinstance(_problems, Unset):
            problems = UNSET
        else:
            problems = ValidationErrorProblems.from_dict(_problems)

        validation_error = cls(
            problems=problems,
        )

        validation_error.additional_properties = d
        return validation_error

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
