from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tool_call import ToolCall


T = TypeVar("T", bound="ConsolidationCompletionEvent")


@_attrs_define
class ConsolidationCompletionEvent:
    """A completion event emitted during memory consolidation.
    Note: for this stream the `type` field is emitted as an empty string.

        Attributes:
            type_ (str): Always empty for consolidation events.
            done (bool):
            completion (str):
            tool_calls (list[ToolCall]):
    """

    type_: str
    done: bool
    completion: str
    tool_calls: list[ToolCall]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        done = self.done

        completion = self.completion

        tool_calls = []
        for tool_calls_item_data in self.tool_calls:
            tool_calls_item = tool_calls_item_data.to_dict()
            tool_calls.append(tool_calls_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "done": done,
                "completion": completion,
                "tool_calls": tool_calls,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_call import ToolCall

        d = dict(src_dict)
        type_ = d.pop("type")

        done = d.pop("done")

        completion = d.pop("completion")

        tool_calls = []
        _tool_calls = d.pop("tool_calls")
        for tool_calls_item_data in _tool_calls:
            tool_calls_item = ToolCall.from_dict(tool_calls_item_data)

            tool_calls.append(tool_calls_item)

        consolidation_completion_event = cls(
            type_=type_,
            done=done,
            completion=completion,
            tool_calls=tool_calls,
        )

        consolidation_completion_event.additional_properties = d
        return consolidation_completion_event

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
