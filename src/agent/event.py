import json
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Protocol, Self

import agent.tool as tool
import arch_agent.api.tool_results.resolve_tool_call as tool_result
import arch_agent.client as agent_client
import arch_agent.models as models


class EventType(Protocol):
    @classmethod
    def from_dict(cls, data: Mapping[str, Any], /) -> Self: ...


_EVENT_TYPE_MAP: dict[str, type[EventType]] = {
    "loop_exit": models.LoopExitEvent,
    "complete": models.CompletionEvent,
    "complete_mistake": models.CompletionMistakeEvent,
    "compaction": models.CompactionEvent,
    "tool_error": models.ToolErrorEvent,
    "provided_toolcall": models.ProvidedToolCallEvent,
    "tool_result": models.ToolResultEvent,
}


class EventHandler(ABC):
    @abstractmethod
    def process_loop_exit(self, event: models.LoopExitEvent):
        pass

    @abstractmethod
    def process_compaction(self, event: models.CompactionEvent):
        pass

    @abstractmethod
    def process_completion(self, event: models.CompletionEvent):
        pass

    @abstractmethod
    def process_completion_mistake(self, event: models.CompletionMistakeEvent):
        pass

    @abstractmethod
    def process_tool_error(self, event: models.ToolErrorEvent):
        pass

    @abstractmethod
    def process_tool_result(self, event: models.ToolResultEvent):
        pass

    @abstractmethod
    def process_error(self, err: models.Error):
        pass


def determine_response(data: str) -> EventType | None:
    if "data: [DONE]" in data:
        return None

    if data.startswith("data:"):
        raw_str = data.removeprefix("data: ")
        event_dict = json.loads(raw_str)
        event_type_name = event_dict.get("type")
        event_type = _EVENT_TYPE_MAP.get(event_type_name)
        if event_type is None:
            raise ValueError(f"unknown result type {event_type_name}")

        return event_type.from_dict(event_dict)

    if data.startswith("error:"):
        raw_str = data.removeprefix("error: ")
        error_dict = json.loads(raw_str)
        return models.Error.from_dict(error_dict)


class AgentEventHandler:
    _tools_map: dict[str, tool.SafeTool]
    _client: agent_client.Client
    _event_handler: EventHandler

    def __init__(
        self,
        client: agent_client.Client,
        event_handler: EventHandler,
        provided_tools: list[tool.SafeTool],
    ) -> None:
        self._event_handler = event_handler
        self._client = client
        for t in provided_tools:
            self._tools_map[t.name()] = t

    def allowed_tool_servers(self) -> list[models.ProvidedToolServer]:

        allowed_tools: list[models.ProvidedTool] = []
        for t in self._tools_map.values():
            allowed_tools.append(
                models.ProvidedTool(
                    name=t.name(),
                    description=t.description(),
                    schema=models.ProvidedToolSchema.from_dict(t.schema()),
                )
            )

        return [models.ProvidedToolServer(tools=allowed_tools)]

    def process_event(self, event: EventType):
        match event:
            case models.ProvidedToolCallEvent():
                self._process_provided_toolcall(event)

            case models.CompactionEvent():
                self._event_handler.process_compaction(event)

            case models.CompletionEvent():
                self._event_handler.process_completion(event)

            case models.CompletionMistakeEvent():
                self._event_handler.process_completion_mistake(event)

            case models.LoopExitEvent():
                self._event_handler.process_loop_exit(event)

            case models.ToolResultEvent():
                self._event_handler.process_tool_result(event)

            case models.ToolErrorEvent():
                self._event_handler.process_tool_error(event)

            case models.Error():
                self._event_handler.process_error(event)

            case _:
                raise Exception(f"unexpected event: {type(event)}")

    def _process_provided_toolcall(self, event: models.ProvidedToolCallEvent):
        result: str

        tool = self._tools_map.get(event.tool)
        if tool is None:
            result = f"tool '{tool}' is not exist"

        else:
            args: dict[str, Any] = {}

            if isinstance(event.args, models.ProvidedToolCallEventArgs):
                args = event.args.to_dict()

            try:
                result = tool.execute(args)
            except Exception as e:
                result = f"tool error: {e}"

        content_part = models.ContentPart(text=result)
        answer = models.ToolResultPayload(result=[content_part])

        result_id: str = event.result_id if isinstance(event.result_id, str) else ""

        tool_result.sync(
            id=result_id,
            body=answer,
            client=self._client,
        )


class ConsolidationEventHandler(ABC):
    def __init__(self) -> None:
        super().__init__()

    def process_event(self, event: EventType):
        match event:
            case models.CompletionEvent():
                self._process_completion(event)

            case models.Error():
                self._process_error(event)

            case _:
                raise Exception(f"unexpected event: {type(event)}")

    @abstractmethod
    def _process_completion(self, event: models.CompletionEvent):
        pass

    @abstractmethod
    def _process_error(self, err: models.Error):
        pass
