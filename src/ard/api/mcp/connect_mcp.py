from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.server_gateway_config import ServerGatewayConfig
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    mcp: str,
    *,
    body: ServerGatewayConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mcp/{mcp}".format(
            mcp=quote(str(mcp), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ValidationError | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = ValidationError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Response[Any | ValidationError]:
    """Connect an MCP server

     Connects (or replaces) an MCP server with the ID given in the path.
    Two connection methods are supported:
    - `http_gateway`: connect to a remote MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        mcp (str):
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ValidationError]
    """

    kwargs = _get_kwargs(
        mcp=mcp,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Any | ValidationError | None:
    """Connect an MCP server

     Connects (or replaces) an MCP server with the ID given in the path.
    Two connection methods are supported:
    - `http_gateway`: connect to a remote MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        mcp (str):
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ValidationError
    """

    return sync_detailed(
        mcp=mcp,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Response[Any | ValidationError]:
    """Connect an MCP server

     Connects (or replaces) an MCP server with the ID given in the path.
    Two connection methods are supported:
    - `http_gateway`: connect to a remote MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        mcp (str):
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ValidationError]
    """

    kwargs = _get_kwargs(
        mcp=mcp,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServerGatewayConfig,
) -> Any | ValidationError | None:
    """Connect an MCP server

     Connects (or replaces) an MCP server with the ID given in the path.
    Two connection methods are supported:
    - `http_gateway`: connect to a remote MCP server via URL.
    - `command_gateway`: spawn a local MCP server process.
    Exactly one of `http_gateway` or `command_gateway` must be provided.

    Args:
        mcp (str):
        body (ServerGatewayConfig): Exactly one of `http_gateway` or `command_gateway` must be
            provided.
            If neither or both are provided, the request is rejected with 400.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ValidationError
    """

    return (
        await asyncio_detailed(
            mcp=mcp,
            client=client,
            body=body,
        )
    ).parsed
