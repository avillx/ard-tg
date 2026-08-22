from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.completion_dto import CompletionDTO
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    agent: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/memory/{agent}/consolidate".format(
            agent=quote(str(agent), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CompletionDTO | Error | None:
    if response.status_code == 200:
        response_200 = CompletionDTO.from_dict(response.text)

        return response_200

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CompletionDTO | Error]:
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
) -> Response[CompletionDTO | Error]:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompletionDTO | Error]
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
) -> CompletionDTO | Error | None:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompletionDTO | Error
    """

    return sync_detailed(
        agent=agent,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[CompletionDTO | Error]:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompletionDTO | Error]
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
) -> CompletionDTO | Error | None:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompletionDTO | Error
    """

    return (
        await asyncio_detailed(
            agent=agent,
            client=client,
        )
    ).parsed
