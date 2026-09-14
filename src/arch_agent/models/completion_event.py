from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.completion_event_type import CompletionEventType

if TYPE_CHECKING:
    from ..models.tool_call import ToolCall


T = TypeVar("T", bound="CompletionEvent")


@_attrs_define
class CompletionEvent:
    """A successful completion chunk. Emitted with type `complete`.

    Attributes:
        type_ (CompletionEventType):
        done (bool): Whether this is the final completion chunk.
        completion (str): The completion text chunk.
        tool_calls (list[ToolCall]): Tool calls made by the model.
    """

    type_: CompletionEventType
    done: bool
    completion: str
    tool_calls: list[ToolCall]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

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
        type_ = CompletionEventType(d.pop("type"))

        done = d.pop("done")

        completion = d.pop("completion")

        tool_calls = []
        _tool_calls = d.pop("tool_calls")
        for tool_calls_item_data in _tool_calls:
            tool_calls_item = ToolCall.from_dict(tool_calls_item_data)

            tool_calls.append(tool_calls_item)

        completion_event = cls(
            type_=type_,
            done=done,
            completion=completion,
            tool_calls=tool_calls,
        )

        completion_event.additional_properties = d
        return completion_event

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
