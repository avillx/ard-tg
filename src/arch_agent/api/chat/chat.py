from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_body import ChatBody
from ...models.compaction_event import CompactionEvent
from ...models.completion_event import CompletionEvent
from ...models.completion_mistake_event import CompletionMistakeEvent
from ...models.loop_exit_event import LoopExitEvent
from ...models.provided_tool_call_event import ProvidedToolCallEvent
from ...models.tool_error_event import ToolErrorEvent
from ...models.tool_result_event import ToolResultEvent
from ...types import Response


def _get_kwargs(
    agent: str,
    session: str,
    *,
    body: ChatBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/chat/{agent}/{session}".format(
            agent=quote(str(agent), safe=""),
            session=quote(str(session), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            CompactionEvent
            | CompletionEvent
            | CompletionMistakeEvent
            | LoopExitEvent
            | ProvidedToolCallEvent
            | ToolErrorEvent
            | ToolResultEvent
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_0 = CompletionEvent.from_dict(data)

                return componentsschemas_chat_event_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_1 = CompletionMistakeEvent.from_dict(data)

                return componentsschemas_chat_event_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_2 = ToolErrorEvent.from_dict(data)

                return componentsschemas_chat_event_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_3 = ToolResultEvent.from_dict(data)

                return componentsschemas_chat_event_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_4 = LoopExitEvent.from_dict(data)

                return componentsschemas_chat_event_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_chat_event_type_5 = CompactionEvent.from_dict(data)

                return componentsschemas_chat_event_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_chat_event_type_6 = ProvidedToolCallEvent.from_dict(data)

            return componentsschemas_chat_event_type_6

        response_200 = _parse_response_200(response.text)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    agent: str,
    session: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> Response[
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
]:
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        agent (str):
        session (str):
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompactionEvent | CompletionEvent | CompletionMistakeEvent | LoopExitEvent | ProvidedToolCallEvent | ToolErrorEvent | ToolResultEvent]
    """

    kwargs = _get_kwargs(
        agent=agent,
        session=session,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent: str,
    session: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> (
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
    | None
):
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        agent (str):
        session (str):
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompactionEvent | CompletionEvent | CompletionMistakeEvent | LoopExitEvent | ProvidedToolCallEvent | ToolErrorEvent | ToolResultEvent
    """

    return sync_detailed(
        agent=agent,
        session=session,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    agent: str,
    session: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> Response[
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
]:
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        agent (str):
        session (str):
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompactionEvent | CompletionEvent | CompletionMistakeEvent | LoopExitEvent | ProvidedToolCallEvent | ToolErrorEvent | ToolResultEvent]
    """

    kwargs = _get_kwargs(
        agent=agent,
        session=session,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent: str,
    session: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatBody,
) -> (
    CompactionEvent
    | CompletionEvent
    | CompletionMistakeEvent
    | LoopExitEvent
    | ProvidedToolCallEvent
    | ToolErrorEvent
    | ToolResultEvent
    | None
):
    """Start a chat completion

     Initiates an agent chat completion and streams events via Server-Sent Events (SSE).
    The response is a stream of JSON envelopes, one per line, prefixed with `data: `.
    The stream ends with `data: [DONE]`.

    Args:
        agent (str):
        session (str):
        body (ChatBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompactionEvent | CompletionEvent | CompletionMistakeEvent | LoopExitEvent | ProvidedToolCallEvent | ToolErrorEvent | ToolResultEvent
    """

    return (
        await asyncio_detailed(
            agent=agent,
            session=session,
            client=client,
            body=body,
        )
    ).parsed
