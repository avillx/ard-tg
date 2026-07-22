from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.activity_record import ActivityRecord


T = TypeVar("T", bound="ActivityLogsResponse")


@_attrs_define
class ActivityLogsResponse:
    """Activity logs for a time period.

    Example:
        {'activity': [{'date': '2025-01-01', 'content': 'Agent processed task: daily_report'}]}

    Attributes:
        activity (list[ActivityRecord] | Unset):
    """

    activity: list[ActivityRecord] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activity: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.activity, Unset):
            activity = []
            for activity_item_data in self.activity:
                activity_item = activity_item_data.to_dict()
                activity.append(activity_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if activity is not UNSET:
            field_dict["activity"] = activity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activity_record import ActivityRecord

        d = dict(src_dict)
        _activity = d.pop("activity", UNSET)
        activity: list[ActivityRecord] | Unset = UNSET
        if _activity is not UNSET:
            activity = []
            for activity_item_data in _activity:
                activity_item = ActivityRecord.from_dict(activity_item_data)

                activity.append(activity_item)

        activity_logs_response = cls(
            activity=activity,
        )

        activity_logs_response.additional_properties = d
        return activity_logs_response

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
