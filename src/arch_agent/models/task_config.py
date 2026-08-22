from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskConfig")


@_attrs_define
class TaskConfig:
    """Configuration for a periodic autonomous task.
    Tasks are executed on a cron schedule and send requests to agent recipients.

        Example:
            {'name': 'daily_report', 'description': 'Generate daily activity report', 'recipients': ['agent_main'],
                'schedule': '0 9 * * 1', 'request': 'Generate the daily report', 'active': True, 'oneshot': False}

        Attributes:
            name (str):
            description (str):
            recipients (list[str]): Agent IDs that receive the task.
            schedule (str): Cron expression (5-field: minute hour day month weekday). Supports standard 5-field cron syntax
                including step values (e.g. `*/15`). Example: 0 9 * * 1.
            request (str): The task request text.
            active (bool | Unset): Whether the task is active. Default: False.
            oneshot (bool | Unset): Whether the task runs only once. Default: False.
    """

    name: str
    description: str
    recipients: list[str]
    schedule: str
    request: str
    active: bool | Unset = False
    oneshot: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        recipients = self.recipients

        schedule = self.schedule

        request = self.request

        active = self.active

        oneshot = self.oneshot

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "recipients": recipients,
                "schedule": schedule,
                "request": request,
            }
        )
        if active is not UNSET:
            field_dict["active"] = active
        if oneshot is not UNSET:
            field_dict["oneshot"] = oneshot

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        recipients = cast(list[str], d.pop("recipients"))

        schedule = d.pop("schedule")

        request = d.pop("request")

        active = d.pop("active", UNSET)

        oneshot = d.pop("oneshot", UNSET)

        task_config = cls(
            name=name,
            description=description,
            recipients=recipients,
            schedule=schedule,
            request=request,
            active=active,
            oneshot=oneshot,
        )

        task_config.additional_properties = d
        return task_config

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
