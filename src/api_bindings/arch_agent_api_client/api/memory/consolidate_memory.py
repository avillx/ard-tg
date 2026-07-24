from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_compaction_event import ChatCompactionEvent
from ...models.chat_completion_event import ChatCompletionEvent
from ...models.chat_error_event import ChatErrorEvent
from ...models.chat_provided_tool_call_event import ChatProvidedToolCallEvent
from ...models.chat_tool_result_event import ChatToolResultEvent
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


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ChatCompactionEvent
    | ChatCompletionEvent
    | ChatErrorEvent
    | ChatProvidedToolCallEvent
    | ChatToolResultEvent
    | Error
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_0 = ChatErrorEvent.from_dict(data)

                return componentsschemas_chat_event_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_1 = ChatCompletionEvent.from_dict(data)

                return componentsschemas_chat_event_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_2 = ChatToolResultEvent.from_dict(data)

                return componentsschemas_chat_event_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_3 = ChatCompactionEvent.from_dict(data)

                return componentsschemas_chat_event_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_chat_event_type_4 = ChatProvidedToolCallEvent.from_dict(data)

            return componentsschemas_chat_event_type_4

        response_200 = _parse_response_200(response.text)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error
]:
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
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error
]:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error]
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
) -> (
    ChatCompactionEvent
    | ChatCompletionEvent
    | ChatErrorEvent
    | ChatProvidedToolCallEvent
    | ChatToolResultEvent
    | Error
    | None
):
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error
    """

    return sync_detailed(
        agent=agent,
        client=client,
    ).parsed


async def asyncio_detailed(
    agent: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error
]:
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error]
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
) -> (
    ChatCompactionEvent
    | ChatCompletionEvent
    | ChatErrorEvent
    | ChatProvidedToolCallEvent
    | ChatToolResultEvent
    | Error
    | None
):
    """Consolidate memory for an agent

     Triggers memory consolidation as an SSE stream.
    Returns completion events as the consolidation agent runs.

    Args:
        agent (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | Error
    """

    return (
        await asyncio_detailed(
            agent=agent,
            client=client,
        )
    ).parsed
