from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_call import ToolCall


T = TypeVar("T", bound="ChatCompletionPayload")


@_attrs_define
class ChatCompletionPayload:
    """Payload of a completion event in the chat stream.

    Example:
        {'done': False, 'completion': 'Hello!', 'tool_calls': []}

    Attributes:
        done (bool | Unset): Whether this is the final completion chunk.
        completion (str | Unset): The completion text chunk.
        tool_calls (list[ToolCall] | Unset): Tool calls made by the model (non-empty only on done chunks).
    """

    done: bool | Unset = UNSET
    completion: str | Unset = UNSET
    tool_calls: list[ToolCall] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        done = self.done

        completion = self.completion

        tool_calls: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tool_calls, Unset):
            tool_calls = []
            for tool_calls_item_data in self.tool_calls:
                tool_calls_item = tool_calls_item_data.to_dict()
                tool_calls.append(tool_calls_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if done is not UNSET:
            field_dict["done"] = done
        if completion is not UNSET:
            field_dict["completion"] = completion
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_call import ToolCall

        d = dict(src_dict)
        done = d.pop("done", UNSET)

        completion = d.pop("completion", UNSET)

        _tool_calls = d.pop("tool_calls", UNSET)
        tool_calls: list[ToolCall] | Unset = UNSET
        if _tool_calls is not UNSET:
            tool_calls = []
            for tool_calls_item_data in _tool_calls:
                tool_calls_item = ToolCall.from_dict(tool_calls_item_data)

                tool_calls.append(tool_calls_item)

        chat_completion_payload = cls(
            done=done,
            completion=completion,
            tool_calls=tool_calls,
        )

        chat_completion_payload.additional_properties = d
        return chat_completion_payload

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
