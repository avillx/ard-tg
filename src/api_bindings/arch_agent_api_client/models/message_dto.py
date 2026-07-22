from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_dto_role import MessageDTORole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.content_part import ContentPart
    from ..models.tool_call import ToolCall


T = TypeVar("T", bound="MessageDTO")


@_attrs_define
class MessageDTO:
    """A single message in a session conversation.

    Example:
        {'role': 'user', 'content': [{'text': 'Read the report'}]}

    Attributes:
        role (MessageDTORole | Unset): Message role: `agent` (assistant response), `user`, `tool` (tool result), or
            `system`.
        content (list[ContentPart] | Unset):
        tool_calls (list[ToolCall] | Unset):
    """

    role: MessageDTORole | Unset = UNSET
    content: list[ContentPart] | Unset = UNSET
    tool_calls: list[ToolCall] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        content: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = []
            for content_item_data in self.content:
                content_item = content_item_data.to_dict()
                content.append(content_item)

        tool_calls: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tool_calls, Unset):
            tool_calls = []
            for tool_calls_item_data in self.tool_calls:
                tool_calls_item = tool_calls_item_data.to_dict()
                tool_calls.append(tool_calls_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if content is not UNSET:
            field_dict["content"] = content
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.content_part import ContentPart
        from ..models.tool_call import ToolCall

        d = dict(src_dict)
        _role = d.pop("role", UNSET)
        role: MessageDTORole | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = MessageDTORole(_role)

        _content = d.pop("content", UNSET)
        content: list[ContentPart] | Unset = UNSET
        if _content is not UNSET:
            content = []
            for content_item_data in _content:
                content_item = ContentPart.from_dict(content_item_data)

                content.append(content_item)

        _tool_calls = d.pop("tool_calls", UNSET)
        tool_calls: list[ToolCall] | Unset = UNSET
        if _tool_calls is not UNSET:
            tool_calls = []
            for tool_calls_item_data in _tool_calls:
                tool_calls_item = ToolCall.from_dict(tool_calls_item_data)

                tool_calls.append(tool_calls_item)

        message_dto = cls(
            role=role,
            content=content,
            tool_calls=tool_calls,
        )

        message_dto.additional_properties = d
        return message_dto

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
