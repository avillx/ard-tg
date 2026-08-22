from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.mcp_connect_response import MCPConnectResponse
from ...models.server_gateway_config import ServerGatewayConfig
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: ServerGatewayConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mcp",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ValidationError | MCPConnectResponse | None:
    if response.status_code == 200:
        response_200 = MCPConnectResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:

        def _parse_response_400(data: object) -> Error | ValidationError:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_400_type_0 = Error.from_dict(data)

                return response_400_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_400_type_1 = ValidationError.from_dict(data)

            return response_400_type_1

        response_400 = _parse_response_400(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ValidationError | MCPConnectResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Response[Error | ValidationError | MCPConnectResponse]:
    """Connect an MCP server

     Connects an MCP server. Two connection methods are supported:
    - `http_gateway`: connect to a remote SSE-based MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.
             Example: {'http_gateway': {'url': 'http://localhost:3001/mcp', 'token': 'secret-token'}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ValidationError | MCPConnectResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Error | ValidationError | MCPConnectResponse | None:
    """Connect an MCP server

     Connects an MCP server. Two connection methods are supported:
    - `http_gateway`: connect to a remote SSE-based MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.
             Example: {'http_gateway': {'url': 'http://localhost:3001/mcp', 'token': 'secret-token'}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ValidationError | MCPConnectResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Response[Error | ValidationError | MCPConnectResponse]:
    """Connect an MCP server

     Connects an MCP server. Two connection methods are supported:
    - `http_gateway`: connect to a remote SSE-based MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.
             Example: {'http_gateway': {'url': 'http://localhost:3001/mcp', 'token': 'secret-token'}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ValidationError | MCPConnectResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Error | ValidationError | MCPConnectResponse | None:
    """Connect an MCP server

     Connects an MCP server. Two connection methods are supported:
    - `http_gateway`: connect to a remote SSE-based MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.
             Example: {'http_gateway': {'url': 'http://localhost:3001/mcp', 'token': 'secret-token'}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ValidationError | MCPConnectResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
