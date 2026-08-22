from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from .server_gateway_config_command_gateway import ServerGatewayConfigCommandGateway
    from .server_gateway_config_http_gateway import ServerGatewayConfigHttpGateway


T = TypeVar("T", bound="ServerGatewayConfig")


@_attrs_define
class ServerGatewayConfig:
    """Exactly one of `http_gateway` or `command_gateway` must be provided.
    If neither or both are provided, the request is rejected with 400.

        Example:
            {'http_gateway': {'url': 'http://localhost:3001/mcp', 'token': 'secret-token'}}

        Attributes:
            http_gateway (ServerGatewayConfigHttpGateway | Unset): Connect to a remote SSE-based MCP server via URL.
            command_gateway (ServerGatewayConfigCommandGateway | Unset): Spawn a local MCP server process.
    """

    http_gateway: ServerGatewayConfigHttpGateway | Unset = UNSET
    command_gateway: ServerGatewayConfigCommandGateway | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        http_gateway: dict[str, Any] | Unset = UNSET
        if not isinstance(self.http_gateway, Unset):
            http_gateway = self.http_gateway.to_dict()

        command_gateway: dict[str, Any] | Unset = UNSET
        if not isinstance(self.command_gateway, Unset):
            command_gateway = self.command_gateway.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if http_gateway is not UNSET:
            field_dict["http_gateway"] = http_gateway
        if command_gateway is not UNSET:
            field_dict["command_gateway"] = command_gateway

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from .server_gateway_config_command_gateway import ServerGatewayConfigCommandGateway
        from .server_gateway_config_http_gateway import ServerGatewayConfigHttpGateway

        d = dict(src_dict)
        _http_gateway = d.pop("http_gateway", UNSET)
        http_gateway: ServerGatewayConfigHttpGateway | Unset
        if isinstance(_http_gateway, Unset):
            http_gateway = UNSET
        else:
            http_gateway = ServerGatewayConfigHttpGateway.from_dict(_http_gateway)

        _command_gateway = d.pop("command_gateway", UNSET)
        command_gateway: ServerGatewayConfigCommandGateway | Unset
        if isinstance(_command_gateway, Unset):
            command_gateway = UNSET
        else:
            command_gateway = ServerGatewayConfigCommandGateway.from_dict(_command_gateway)

        server_gateway_config = cls(
            http_gateway=http_gateway,
            command_gateway=command_gateway,
        )

        server_gateway_config.additional_properties = d
        return server_gateway_config

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
