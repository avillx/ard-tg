from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    mcp: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/mcp/{mcp}".format(
            mcp=quote(str(mcp), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error]:
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
) -> Response[Any | Error]:
    """Disconnect an MCP server

     Disconnects an MCP server by ID. The server's tools become unavailable
    to agents after disconnection.

    Args:
        mcp (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        mcp=mcp,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | None:
    """Disconnect an MCP server

     Disconnects an MCP server by ID. The server's tools become unavailable
    to agents after disconnection.

    Args:
        mcp (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        mcp=mcp,
        client=client,
    ).parsed


async def asyncio_detailed(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Error]:
    """Disconnect an MCP server

     Disconnects an MCP server by ID. The server's tools become unavailable
    to agents after disconnection.

    Args:
        mcp (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        mcp=mcp,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mcp: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | None:
    """Disconnect an MCP server

     Disconnects an MCP server by ID. The server's tools become unavailable
    to agents after disconnection.

    Args:
        mcp (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            mcp=mcp,
            client=client,
        )
    ).parsed
