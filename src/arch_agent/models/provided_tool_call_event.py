from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .provided_tool_call_event_type import ProvidedToolCallEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .provided_tool_call_event_args import ProvidedToolCallEventArgs


T = TypeVar("T", bound="ProvidedToolCallEvent")


@_attrs_define
class ProvidedToolCallEvent:
    """The agent called a client-provided tool. Emitted with type `provided_toolcall`.

    Example:
        {'type': 'provided_toolcall', 'tool': 'my_tool', 'args': {}, 'result_id': 'fg1ds12sg3d3f3fg342234d', 'agent_id':
            'agent_1', 'session_id': 'sess_1'}

    Attributes:
        type_ (ProvidedToolCallEventType):
        tool (str): Tool name.
        agent_id (str): Agent identifier.
        session_id (str): Session identifier.
        args (ProvidedToolCallEventArgs | Unset): Tool arguments.
        result_id (str | Unset): URL-safe id for calling the /toolresult/{id} endpoint to resolve this call.
    """

    type_: ProvidedToolCallEventType
    tool: str
    agent_id: str
    session_id: str
    args: ProvidedToolCallEventArgs | Unset = UNSET
    result_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        tool = self.tool

        agent_id = self.agent_id

        session_id = self.session_id

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        result_id = self.result_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "tool": tool,
                "agent_id": agent_id,
                "session_id": session_id,
            }
        )
        if args is not UNSET:
            field_dict["args"] = args
        if result_id is not UNSET:
            field_dict["result_id"] = result_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .provided_tool_call_event_args import ProvidedToolCallEventArgs

        d = dict(src_dict)
        type_ = ProvidedToolCallEventType(d.pop("type"))

        tool = d.pop("tool")

        agent_id = d.pop("agent_id")

        session_id = d.pop("session_id")

        _args = d.pop("args", UNSET)
        args: ProvidedToolCallEventArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = ProvidedToolCallEventArgs.from_dict(_args)

        result_id = d.pop("result_id", UNSET)

        provided_tool_call_event = cls(
            type_=type_,
            tool=tool,
            agent_id=agent_id,
            session_id=session_id,
            args=args,
            result_id=result_id,
        )

        provided_tool_call_event.additional_properties = d
        return provided_tool_call_event

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
