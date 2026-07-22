from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_provided_tool_call_payload_args import ChatProvidedToolCallPayloadArgs


T = TypeVar("T", bound="ChatProvidedToolCallPayload")


@_attrs_define
class ChatProvidedToolCallPayload:
    """Payload of a provided tool call event in the chat stream.

    Example:
        {'tool': 'my_tool', 'args': {}, 'result_link': 'http://host/api/v1/toolresult/abc', 'agent_id': 'agent_1',
            'session_id': 'sess_1'}

    Attributes:
        tool (str | Unset): Tool name.
        args (ChatProvidedToolCallPayloadArgs | Unset): Tool arguments.
        result_link (str | Unset): URL for the external tool server to POST the result back.
        agent_id (str | Unset): Agent identifier.
        session_id (str | Unset): Session identifier.
    """

    tool: str | Unset = UNSET
    args: ChatProvidedToolCallPayloadArgs | Unset = UNSET
    result_link: str | Unset = UNSET
    agent_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool = self.tool

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        result_link = self.result_link

        agent_id = self.agent_id

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tool is not UNSET:
            field_dict["tool"] = tool
        if args is not UNSET:
            field_dict["args"] = args
        if result_link is not UNSET:
            field_dict["result_link"] = result_link
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_provided_tool_call_payload_args import ChatProvidedToolCallPayloadArgs

        d = dict(src_dict)
        tool = d.pop("tool", UNSET)

        _args = d.pop("args", UNSET)
        args: ChatProvidedToolCallPayloadArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = ChatProvidedToolCallPayloadArgs.from_dict(_args)

        result_link = d.pop("result_link", UNSET)

        agent_id = d.pop("agent_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        chat_provided_tool_call_payload = cls(
            tool=tool,
            args=args,
            result_link=result_link,
            agent_id=agent_id,
            session_id=session_id,
        )

        chat_provided_tool_call_payload.additional_properties = d
        return chat_provided_tool_call_payload

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
