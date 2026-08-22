from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.session import Session
from ...types import Response


def _get_kwargs(
    agent: str,
    session_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/session/{agent}/{session_id}".format(
            agent=quote(str(agent), safe=""),
            session_id=quote(str(session_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | Session | None:
    if response.status_code == 200:
        response_200 = Session.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | Session]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Session]:
    """Get a session by ID

     Returns the full session data including message history, token usage, and timestamps.

    Args:
        agent (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Session]
    """

    kwargs = _get_kwargs(
        agent=agent,
        session_id=session_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Session | None:
    """Get a session by ID

     Returns the full session data including message history, token usage, and timestamps.

    Args:
        agent (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Session
    """

    return sync_detailed(
        agent=agent,
        session_id=session_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Session]:
    """Get a session by ID

     Returns the full session data including message history, token usage, and timestamps.

    Args:
        agent (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Session]
    """

    kwargs = _get_kwargs(
        agent=agent,
        session_id=session_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Session | None:
    """Get a session by ID

     Returns the full session data including message history, token usage, and timestamps.

    Args:
        agent (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Session
    """

    return (
        await asyncio_detailed(
            agent=agent,
            session_id=session_id,
            client=client,
        )
    ).parsed
