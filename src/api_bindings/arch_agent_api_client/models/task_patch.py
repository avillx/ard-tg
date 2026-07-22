from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskPatch")


@_attrs_define
class TaskPatch:
    """Partial update for a task. Only supplied fields are updated. Fields set to `null` are ignored.

    Example:
        {'active': False}

    Attributes:
        active (bool | None | Unset):
        name (None | str | Unset):
        description (None | str | Unset):
        recipients (list[str] | None | Unset):
        schedule (None | str | Unset):
        request (None | str | Unset):
        oneshot (bool | None | Unset):
    """

    active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    recipients: list[str] | None | Unset = UNSET
    schedule: None | str | Unset = UNSET
    request: None | str | Unset = UNSET
    oneshot: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active: bool | None | Unset
        if isinstance(self.active, Unset):
            active = UNSET
        else:
            active = self.active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        recipients: list[str] | None | Unset
        if isinstance(self.recipients, Unset):
            recipients = UNSET
        elif isinstance(self.recipients, list):
            recipients = self.recipients

        else:
            recipients = self.recipients

        schedule: None | str | Unset
        if isinstance(self.schedule, Unset):
            schedule = UNSET
        else:
            schedule = self.schedule

        request: None | str | Unset
        if isinstance(self.request, Unset):
            request = UNSET
        else:
            request = self.request

        oneshot: bool | None | Unset
        if isinstance(self.oneshot, Unset):
            oneshot = UNSET
        else:
            oneshot = self.oneshot

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active is not UNSET:
            field_dict["active"] = active
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if recipients is not UNSET:
            field_dict["recipients"] = recipients
        if schedule is not UNSET:
            field_dict["schedule"] = schedule
        if request is not UNSET:
            field_dict["request"] = request
        if oneshot is not UNSET:
            field_dict["oneshot"] = oneshot

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        active = _parse_active(d.pop("active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_recipients(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                recipients_type_0 = cast(list[str], data)

                return recipients_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        recipients = _parse_recipients(d.pop("recipients", UNSET))

        def _parse_schedule(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        schedule = _parse_schedule(d.pop("schedule", UNSET))

        def _parse_request(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        request = _parse_request(d.pop("request", UNSET))

        def _parse_oneshot(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        oneshot = _parse_oneshot(d.pop("oneshot", UNSET))

        task_patch = cls(
            active=active,
            name=name,
            description=description,
            recipients=recipients,
            schedule=schedule,
            request=request,
            oneshot=oneshot,
        )

        task_patch.additional_properties = d
        return task_patch

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
