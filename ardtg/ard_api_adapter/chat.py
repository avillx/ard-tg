import json
from typing import TYPE_CHECKING, Any, Protocol, Self, cast, override

import ardtg.ard_api.models as models
from ardtg.domain.chat import (
    ChatStreamer,
    CompactionEvent,
    CompletionEvent,
    CompletionMistakeEvent,
    ContentPart,
    ErrorEvent,
    Event,
    LoopExitEvent,
    ProvidedToolCallEvent,
    Tool,
    ToolArgs,
    ToolCall,
    ToolErrorEvent,
    ToolResultEvent,
)

if TYPE_CHECKING:
    import logging
    from collections.abc import Iterator, Mapping

    from ardtg.ard_api import Client
    from ardtg.ard_api.types import Unset

_DEFAULT_CHAT_STREAM_TIMEOUT = 10000


class EventType(Protocol):
    @classmethod
    def from_dict(cls, data: Mapping[str, Any], /) -> Self: ...  # pyright: ignore[reportExplicitAny]


_EVENT_TYPE_MAP: dict[str, type[EventType]] = {
    models.LoopExitEventType.LOOP_EXIT: models.LoopExitEvent,
    models.CompletionEventType.COMPLETE: models.CompletionEvent,
    models.CompletionMistakeEventType.COMPLETE_MISTAKE: models.CompletionMistakeEvent,
    models.CompactionEventType.COMPACTION: models.CompactionEvent,
    models.ToolErrorEventType.TOOL_ERROR: models.ToolErrorEvent,
    models.ProvidedToolCallEventType.PROVIDED_TOOLCALL: models.ProvidedToolCallEvent,
    models.ToolResultEventType.TOOL_RESULT: models.ToolResultEvent,
}


def cast_data_to_event(data: str):
    raw_str = data.removeprefix("data: ")
    event_dict = json.loads(raw_str)  # pyright: ignore[reportAny]
    event_type_name: str = event_dict.get("type")  # pyright: ignore[reportAny]
    event_type = _EVENT_TYPE_MAP.get(event_type_name)
    if event_type is None:
        raise ValueError(f"unknown result type {event_type_name}")
    return event_type.from_dict(event_dict)  # pyright: ignore[reportAny]


def cast_data_to_error(data: str):
    raw_str = data.removeprefix("error: ")
    error_dict = json.loads(raw_str)  # pyright: ignore[reportAny]
    return models.Error.from_dict(error_dict)  # pyright: ignore[reportAny]


class StopStream:
    pass


def determine_response(data: str) -> EventType | StopStream:
    if "data: [DONE]" in data:
        return StopStream()

    if data.startswith("data:"):
        return cast_data_to_event(data)

    if data.startswith("error:"):
        return cast_data_to_error(data)

    raise ValueError("unknown data. expect start with 'data:' or 'error:' ")


def cast_tool_args(
    external: models.ProvidedToolCallEventArgs | models.ToolCallArgs | str | Unset,
) -> ToolArgs:

    if isinstance(external, models.ToolCallArgs):
        return external.to_dict()

    if isinstance(external, models.ProvidedToolCallEventArgs):
        return external.to_dict()

    if isinstance(external, str):
        res = json.loads(external)  # pyright: ignore[reportAny]
        if not isinstance(res, dict):
            raise ValueError(f"expected dictionary, got: {type(external).__name__}")
        return cast("ToolArgs", res)

    return {}


def cast_tool_calls(external: list[models.ToolCall]) -> list[ToolCall]:
    return [
        ToolCall(
            args=cast_tool_args(e.args),
            tool=e.tool,
        )
        for e in external
    ]


def cast_to_str(external: str | Unset) -> str:
    return external if isinstance(external, str) else ""


def cast_content_parts(extenral: list[models.ContentPart]) -> list[ContentPart]:
    return [
        ContentPart(
            text=cast_to_str(e.text),
            image_url=cast_to_str(e.image_url),
        )
        for e in extenral
    ]


def cast_to_internal(externtal_event: EventType) -> Event:
    match externtal_event:
        case models.LoopExitEvent():
            cause = externtal_event.cause if isinstance(externtal_event.cause, str) else None
            return LoopExitEvent(
                cause=cause,
            )
        case models.CompletionEvent():
            return CompletionEvent(
                completion=externtal_event.completion,
                done=externtal_event.done,
                tool_calls=cast_tool_calls(externtal_event.tool_calls),
            )
        case models.CompletionMistakeEvent():
            return CompletionMistakeEvent(
                cause=externtal_event.error,
            )
        case models.CompactionEvent():
            return CompactionEvent(
                message=externtal_event.message,
                result=externtal_event.result,
            )
        case models.ToolErrorEvent():
            return ToolErrorEvent(
                tool_name=externtal_event.tool_name,
                args=cast_tool_args(externtal_event.args),
                cause=externtal_event.cause,
            )

        case models.ProvidedToolCallEvent():
            if not isinstance(externtal_event.result_id, str):
                raise ValueError("agent api has no result id")

            return ProvidedToolCallEvent(
                agent_id=externtal_event.agent_id,
                result_id=externtal_event.result_id,
                session_id=externtal_event.session_id,
                tool=externtal_event.tool,
                args=cast_tool_args(externtal_event.args),
            )
        case models.ToolResultEvent():
            return ToolResultEvent(
                content=cast_content_parts(externtal_event.result),
            )
        case models.Error:
            return ErrorEvent(
                cause=cast_to_str(externtal_event.message),
            )
        case _:
            raise ValueError(f"unknown event type {type(externtal_event).__name__}")


def determine_internal_response(data: str) -> Event | StopStream:
    response = determine_response(data)
    if isinstance(response, StopStream):
        return response
    return cast_to_internal(response)


def prepare_tools(tools: list[Tool]) -> list[models.ProvidedToolServer]:

    allowed_tools: list[models.ProvidedTool] = []
    for t in tools:
        allowed_tools.append(
            models.ProvidedTool(
                name=t.name(),
                description=t.description(),
                schema=models.ProvidedToolSchema.from_dict(t.schema()),
            )
        )

    return [models.ProvidedToolServer(tools=allowed_tools)]


def prepare_content_part(content_parts: list[ContentPart]) -> list[models.ContentPart]:
    return [
        models.ContentPart(
            image_url=cp.image_url,
            text=cp.text,
        )
        for cp in content_parts
    ]


class AgentAPIChatStreamer(ChatStreamer):
    _agent_url: str
    _agent_client: Client
    _logger: logging.Logger

    def __init__(
        self,
        agent_url: str,
        agent_client: Client,
        logger: logging.Logger,
    ):
        super().__init__()
        self._logger = logger.getChild("Agent")
        self._agent_url = agent_url
        self._agent_client = agent_client

    def _build_url(self, sesssion_id: str) -> str:
        return "/".join(
            [
                self._agent_url.rstrip("/"),
                "chat",
                sesssion_id,
            ]
        )

    @override
    def chat(
        self,
        *,
        request: ContentPart,
        session_id: str,
        tools: list[Tool],
    ) -> Iterator[Event]:
        """Run the agentic loop with the provided tools _DEFAULT_CHAT_STREAM_TIMEOUT
        All events are processed through the introduced event handler
        """
        chat_body: models.ChatBody = models.ChatBody(
            logging=True,
            user_request=prepare_content_part([request]),
            tool_servers=prepare_tools(tools),
        )

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            url=self._build_url(session_id),
            json=chat_body.to_dict(),
            timeout=_DEFAULT_CHAT_STREAM_TIMEOUT,
        ) as response:
            for line in response.iter_lines():
                # keepalive strings is empty
                if line == "":
                    continue
                ev = determine_internal_response(line)
                if isinstance(ev, StopStream):
                    return
                yield ev
