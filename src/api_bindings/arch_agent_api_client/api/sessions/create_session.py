from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_session_response_201 import CreateSessionResponse201
from ...types import Response


def _get_kwargs(
    agent: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/session/{agent}".format(
            agent=quote(str(agent), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateSessionResponse201 | None:
    if response.status_code == 201:
        response_201 = CreateSessionResponse201.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateSessionResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[CreateSessionResponse201]:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse201]
    """

    kwargs = _get_kwargs(
        agent=agent,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> CreateSessionResponse201 | None:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse201
    """

    return sync_detailed(
        agent=agent,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[CreateSessionResponse201]:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse201]
    """

    kwargs = _get_kwargs(
        agent=agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> CreateSessionResponse201 | None:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse201
    """

    return (
        await asyncio_detailed(
            agent=agent,
            client=client,
        )
    ).parsed
