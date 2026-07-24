from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.content_part import ContentPart
    from ..models.provided_tool_server import ProvidedToolServer


T = TypeVar("T", bound="ChatBody")


@_attrs_define
class ChatBody:
    """
    Attributes:
        agent_id (str): Agent identifier.
        session_id (str): Session identifier.
        user_request (list[ContentPart]): User message content as an array of content parts.
        logging (bool | Unset): Enable logging for this chat invocation. Default: False.
        additional_prompt (str | Unset): Additional prompt text appended to the system prompt.
        tool_servers (list[ProvidedToolServer] | Unset): External client-side tool servers the agent can use for this
            call.
            client guarantee of execution and return result for it on intoduced id
            for tool result endpoint with path parameter
    """

    agent_id: str
    session_id: str
    user_request: list[ContentPart]
    logging: bool | Unset = False
    additional_prompt: str | Unset = UNSET
    tool_servers: list[ProvidedToolServer] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        session_id = self.session_id

        user_request = []
        for user_request_item_data in self.user_request:
            user_request_item = user_request_item_data.to_dict()
            user_request.append(user_request_item)

        logging = self.logging

        additional_prompt = self.additional_prompt

        tool_servers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tool_servers, Unset):
            tool_servers = []
            for tool_servers_item_data in self.tool_servers:
                tool_servers_item = tool_servers_item_data.to_dict()
                tool_servers.append(tool_servers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "session_id": session_id,
                "user_request": user_request,
            }
        )
        if logging is not UNSET:
            field_dict["logging"] = logging
        if additional_prompt is not UNSET:
            field_dict["additional_prompt"] = additional_prompt
        if tool_servers is not UNSET:
            field_dict["tool_servers"] = tool_servers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.content_part import ContentPart
        from ..models.provided_tool_server import ProvidedToolServer

        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        session_id = d.pop("session_id")

        user_request = []
        _user_request = d.pop("user_request")
        for user_request_item_data in _user_request:
            user_request_item = ContentPart.from_dict(user_request_item_data)

            user_request.append(user_request_item)

        logging = d.pop("logging", UNSET)

        additional_prompt = d.pop("additional_prompt", UNSET)

        _tool_servers = d.pop("tool_servers", UNSET)
        tool_servers: list[ProvidedToolServer] | Unset = UNSET
        if _tool_servers is not UNSET:
            tool_servers = []
            for tool_servers_item_data in _tool_servers:
                tool_servers_item = ProvidedToolServer.from_dict(tool_servers_item_data)

                tool_servers.append(tool_servers_item)

        chat_body = cls(
            agent_id=agent_id,
            session_id=session_id,
            user_request=user_request,
            logging=logging,
            additional_prompt=additional_prompt,
            tool_servers=tool_servers,
        )

        chat_body.additional_properties = d
        return chat_body

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
