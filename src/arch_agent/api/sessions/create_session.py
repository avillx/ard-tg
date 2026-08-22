from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_session_body import CreateSessionBody
from ...models.create_session_response_200 import CreateSessionResponse200
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    agent: str,
    *,
    body: CreateSessionBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/session/{agent}".format(
            agent=quote(str(agent), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateSessionResponse200 | Error | None:
    if response.status_code == 200:
        response_200 = CreateSessionResponse200.from_dict(response.json())

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateSessionResponse200 | Error]:
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
    body: CreateSessionBody | Unset = UNSET,
) -> Response[CreateSessionResponse200 | Error]:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):
        body (CreateSessionBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse200 | Error]
    """

    kwargs = _get_kwargs(
        agent=agent,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody | Unset = UNSET,
) -> CreateSessionResponse200 | Error | None:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):
        body (CreateSessionBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse200 | Error
    """

    return sync_detailed(
        agent=agent,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody | Unset = UNSET,
) -> Response[CreateSessionResponse200 | Error]:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):
        body (CreateSessionBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse200 | Error]
    """

    kwargs = _get_kwargs(
        agent=agent,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody | Unset = UNSET,
) -> CreateSessionResponse200 | Error | None:
    """Create a new session

     Creates a new session for the agent. A session holds the conversation history,
    token usage, and metadata. Sessions are used to maintain context across
    multiple chat interactions with the same agent.

    Args:
        agent (str):
        body (CreateSessionBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse200 | Error
    """

    return (
        await asyncio_detailed(
            agent=agent,
            client=client,
            body=body,
        )
    ).parsed
