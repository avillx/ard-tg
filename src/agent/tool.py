from abc import ABC, abstractmethod
from typing import override

from agent.chat import ContentPart, ProvidedToolCallEvent, Tool, ToolResult


class ToolResultSink(ABC):
    @abstractmethod
    def send_result(self,res: ToolResult) -> None:
        pass


class ToolExecutor(ABC):
    @abstractmethod
    def process_provided_toolcall(self, event: ProvidedToolCallEvent):
        pass


class ProvidedToolExecutor(ToolExecutor):
    _tools_map: dict[str, Tool]
    _sink: ToolResultSink

    def __init__(
        self,
        sink: ToolResultSink,
        tools: list[Tool],
    ) -> None:
        self._sink = sink
        self._tools_map = {}
        for t in tools:
            self._tools_map[t.name()] = t


    @override
    def process_provided_toolcall(self, event: ProvidedToolCallEvent):

        text_result = f"tool '{event.tool}' is not exist"
        t = self._tools_map.get(event.tool)
        if t is not None:
            try:
                text_result = t.execute(event.args)
            except Exception as e:  # noqa: BLE001 - tool code is arbitrary
                text_result = f"tool error: {e}"

        content = ContentPart(
            image_url="",
            text=text_result
        )

        result = ToolResult(
            result_id=event.result_id,
            content=[content]
        )

        self._sink.send_result(result)
