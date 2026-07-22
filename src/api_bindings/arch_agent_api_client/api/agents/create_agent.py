from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_config import AgentConfig
from ...models.error import Error
from ...models.message import Message
from ...types import Response


def _get_kwargs(
    agent: str,
    *,
    body: AgentConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agent/{agent}".format(
            agent=quote(str(agent), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | Message | None:
    if response.status_code == 201:
        response_201 = Message.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | Message]:
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
    body: AgentConfig,
) -> Response[Error | Message]:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        agent (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
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
    body: AgentConfig,
) -> Error | Message | None:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        agent (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
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
    body: AgentConfig,
) -> Response[Error | Message]:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        agent (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
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
    body: AgentConfig,
) -> Error | Message | None:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        agent (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
    """

    return (
        await asyncio_detailed(
            agent=agent,
            client=client,
            body=body,
        )
    ).parsed
