from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, override
lazy import logging

from attr import dataclass

import domain.interruption as interruption
import domain.session as session

ToolArgs = dict[str, Any] # pyright: ignore[reportExplicitAny]
ResultID = str
ToolSchema = dict[str, Any] # pyright: ignore[reportExplicitAny]

@dataclass
class ToolResult:
    result_id: ResultID
    content: list[ContentPart]

class Tool(ABC):
    _name: str
    _desctiption: str
    _schema: ToolSchema

    def __init__(
        self,
        name: str,
        description: str,
        schema: ToolSchema
    ):
        self._name = name
        self._desctiption = description
        self._schema = schema


    def name(self) -> str:
        return self._name


    def description(self) -> str:
        return self._desctiption


    def schema(self) -> ToolSchema:
        return self._schema


    @abstractmethod
    def execute(self, args: ToolArgs) -> str:
        pass

@dataclass
class ContentPart:
    image_url: str
    text: str


@dataclass
class ToolCall:
    tool: str
    args: ToolArgs

@dataclass
class Event:
    pass

@dataclass
class LoopExitEvent(Event):
    cause: str | None

@dataclass
class CompletionEvent(Event):
    done: bool
    completion: str
    tool_calls: list[ToolCall]

@dataclass
class CompletionMistakeEvent(Event):
    cause: str

@dataclass
class CompactionEvent(Event):
    message: str
    result: str

@dataclass
class ToolErrorEvent(Event):
    cause: str
    tool_name: str
    args: ToolArgs

@dataclass
class ProvidedToolCallEvent(Event):
    tool: str
    agent_id: str
    session_id: str
    result_id: ResultID
    args: ToolArgs

@dataclass
class ErrorEvent(Event):
    cause: str

@dataclass
class ToolResultEvent(Event):
    content: list[ContentPart]


class EventHandler(ABC):
    @abstractmethod
    def process_loop_exit(self, event: LoopExitEvent):
        pass

    @abstractmethod
    def process_compaction(self, event: CompactionEvent):
        pass

    @abstractmethod
    def process_completion(self, event: CompletionEvent):
        pass

    @abstractmethod
    def process_completion_mistake(self, event: CompletionMistakeEvent):
        pass

    @abstractmethod
    def process_tool_error(self, event: ToolErrorEvent):
        pass

    @abstractmethod
    def process_tool_result(self, event: ToolResultEvent):
        pass

    @abstractmethod
    def process_error(self, err: ErrorEvent):
        pass

    @abstractmethod
    def process_provided_toolcall(self, event: ProvidedToolCallEvent):
        pass

class ChatStreamer(ABC):
    @abstractmethod
    def chat(self,*,request: ContentPart,session_id: str,tools: list[Tool]) -> Iterator[Event]:
        pass

class HandlerError(Exception):
    pass

class Chat(ABC):
    @abstractmethod
    def chat(
        self,
        request: ContentPart,
        event_handler: EventHandler,
        provided_tools: list[Tool],
    ):
        pass

class ChatService(Chat):
    _session_source: session.SessionSource
    _interruptor: interruption.Interruptor
    _logger: logging.Logger
    _chat_streamer: ChatStreamer

    def __init__(
        self,
        session_source: session.SessionSource,
        interruptor: interruption.Interruptor,
        chat_streamer: ChatStreamer,
        logger: logging.Logger,
    ):
        self._logger = logger.getChild("Chat")
        self._session_source = session_source
        self._interruptor = interruptor
        self._chat_streamer = chat_streamer

    @override
    def chat(
        self,
        request: ContentPart,
        event_handler: EventHandler,
        provided_tools: list[Tool],
    ):
        """Run the agentic loop with the provided tools _DEFAULT_CHAT_STREAM_TIMEOUT
        All events are processed through the introduced event handler
        """
        session_id = self._session_source.get_unexpired_session_id()
        self._logger.info("chat started with session: %s",session_id)
        for ev in self._chat_streamer.chat(
            request=request,
            session_id=session_id,
            tools=provided_tools,
        ):
            try:
                self._handle_event(event_handler,ev)
            except Exception as e:
                self._interruptor.interrupt(session_id)
                self._logger.error("event handling error %s",e)
                raise HandlerError() from e

    def _handle_event(self,handler: EventHandler,event: Event):
        match event:
            case ProvidedToolCallEvent():
                handler.process_provided_toolcall(event)

            case CompactionEvent():
                handler.process_compaction(event)

            case CompletionEvent():
                handler.process_completion(event)

            case CompletionMistakeEvent():
                handler.process_completion_mistake(event)

            case LoopExitEvent():
                handler.process_loop_exit(event)

            case ToolResultEvent():
                handler.process_tool_result(event)

            case ToolErrorEvent():
                handler.process_tool_error(event)

            case ErrorEvent():
                handler.process_error(event)

            case _:
                raise Exception(f"unexpected event: {type(event)}")
