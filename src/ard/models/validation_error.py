from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.validation_error_problems_type_0 import ValidationErrorProblemsType0


T = TypeVar("T", bound="ValidationError")


@_attrs_define
class ValidationError:
    """Validation error response with per-field problems.

    Example:
        {'problems': {'schedule': 'invalid cron'}}

    Attributes:
        problems (str | Unset | ValidationErrorProblemsType0):
    """

    problems: str | Unset | ValidationErrorProblemsType0 = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.validation_error_problems_type_0 import ValidationErrorProblemsType0

        problems: dict[str, Any] | str | Unset
        if isinstance(self.problems, Unset):
            problems = UNSET
        elif isinstance(self.problems, ValidationErrorProblemsType0):
            problems = self.problems.to_dict()
        else:
            problems = self.problems

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if problems is not UNSET:
            field_dict["problems"] = problems

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.validation_error_problems_type_0 import ValidationErrorProblemsType0

        d = dict(src_dict)

        def _parse_problems(data: object) -> str | Unset | ValidationErrorProblemsType0:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                problems_type_0 = ValidationErrorProblemsType0.from_dict(data)

                return problems_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | Unset | ValidationErrorProblemsType0, data)

        problems = _parse_problems(d.pop("problems", UNSET))

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
