from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_config import AgentConfig
from ...models.create_agent_response_400 import CreateAgentResponse400
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: AgentConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agent/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | CreateAgentResponse400 | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = CreateAgentResponse400.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | CreateAgentResponse400]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AgentConfig,
) -> Response[Any | CreateAgentResponse400]:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        id (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateAgentResponse400]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AgentConfig,
) -> Any | CreateAgentResponse400 | None:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        id (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateAgentResponse400
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AgentConfig,
) -> Response[Any | CreateAgentResponse400]:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        id (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateAgentResponse400]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AgentConfig,
) -> Any | CreateAgentResponse400 | None:
    """Create an agent

     Creates a new agent with the given ID and configuration.
    The agent ID is chosen by the client. At minimum, a model must be specified.

    Args:
        id (str):
        body (AgentConfig): Configuration for an agent. At minimum, a model must be specified.
            Example: {'model': 'gpt-4', 'memory': True, 'description': 'General assistant',
            'tool_servers': ['filesystem', 'search']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateAgentResponse400
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
