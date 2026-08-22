from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.memory_detail import MemoryDetail
from ...types import Response


def _get_kwargs(
    agent: str,
    memory_name: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/memory/{agent}/{memory_name}".format(
            agent=quote(str(agent), safe=""),
            memory_name=quote(str(memory_name), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | MemoryDetail | None:
    if response.status_code == 200:
        response_200 = MemoryDetail.from_dict(response.json())

        return response_200

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | MemoryDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent: str,
    memory_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | MemoryDetail]:
    """Get a specific memory record

     Returns the full content of a named memory record for the agent.

    Args:
        agent (str):
        memory_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MemoryDetail]
    """

    kwargs = _get_kwargs(
        agent=agent,
        memory_name=memory_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent: str,
    memory_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | MemoryDetail | None:
    """Get a specific memory record

     Returns the full content of a named memory record for the agent.

    Args:
        agent (str):
        memory_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MemoryDetail
    """

    return sync_detailed(
        agent=agent,
        memory_name=memory_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent: str,
    memory_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | MemoryDetail]:
    """Get a specific memory record

     Returns the full content of a named memory record for the agent.

    Args:
        agent (str):
        memory_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MemoryDetail]
    """

    kwargs = _get_kwargs(
        agent=agent,
        memory_name=memory_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent: str,
    memory_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | MemoryDetail | None:
    """Get a specific memory record

     Returns the full content of a named memory record for the agent.

    Args:
        agent (str):
        memory_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MemoryDetail
    """

    return (
        await asyncio_detailed(
            agent=agent,
            memory_name=memory_name,
            client=client,
        )
    ).parsed
