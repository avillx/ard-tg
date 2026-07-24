from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_body import ChatBody
from ...models.chat_compaction_event import ChatCompactionEvent
from ...models.chat_completion_event import ChatCompletionEvent
from ...models.chat_error_event import ChatErrorEvent
from ...models.chat_provided_tool_call_event import ChatProvidedToolCallEvent
from ...models.chat_tool_result_event import ChatToolResultEvent
from ...types import Response


def _get_kwargs(
    *,
    body: ChatBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/chat",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | None
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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
]:
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> (
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | None
):
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> Response[
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
]:
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> (
    ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent | None
):
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompactionEvent | ChatCompletionEvent | ChatErrorEvent | ChatProvidedToolCallEvent | ChatToolResultEvent
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
