from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .completion_dto_type import CompletionDTOType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .tool_call import ToolCall


T = TypeVar("T", bound="CompletionDTO")


@_attrs_define
class CompletionDTO:
    """A completion event emitted during memory consolidation.
    Always has type `complete`.

        Example:
            {'type': 'complete', 'done': True, 'completion': 'Memory consolidated.', 'tool_calls': []}

        Attributes:
            type_ (CompletionDTOType):
            done (bool | Unset): Whether this is the final completion chunk.
            completion (str | Unset): The completion text chunk.
            tool_calls (list[ToolCall] | Unset): Tool calls made by the model (non-empty only on done chunks).
    """

    type_: CompletionDTOType
    done: bool | Unset = UNSET
    completion: str | Unset = UNSET
    tool_calls: list[ToolCall] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

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
        field_dict.update(
            {
                "type": type_,
            }
        )
        if done is not UNSET:
            field_dict["done"] = done
        if completion is not UNSET:
            field_dict["completion"] = completion
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .tool_call import ToolCall

        d = dict(src_dict)
        type_ = CompletionDTOType(d.pop("type"))

        done = d.pop("done", UNSET)

        completion = d.pop("completion", UNSET)

        _tool_calls = d.pop("tool_calls", UNSET)
        tool_calls: list[ToolCall] | Unset = UNSET
        if _tool_calls is not UNSET:
            tool_calls = []
            for tool_calls_item_data in _tool_calls:
                tool_calls_item = ToolCall.from_dict(tool_calls_item_data)

                tool_calls.append(tool_calls_item)

        completion_dto = cls(
            type_=type_,
            done=done,
            completion=completion,
            tool_calls=tool_calls,
        )

        completion_dto.additional_properties = d
        return completion_dto

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
