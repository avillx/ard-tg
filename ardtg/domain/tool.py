from abc import ABC, abstractmethod
from typing import override

from ardtg.domain.chat import ContentPart, ProvidedToolCallEvent, Tool, ToolResult


class ToolResultSink(ABC):
    @abstractmethod
    def send_result(self,res: ToolResult) -> None:
        pass


class ToolExecutor(ABC):
    @abstractmethod
    def process_provided_toolcall(self, tools: list[Tool], event: ProvidedToolCallEvent):
        pass


class ProvidedToolExecutor(ToolExecutor):
    _sink: ToolResultSink

    def __init__(self, sink: ToolResultSink) -> None:
        self._sink = sink

    @override
    def process_provided_toolcall(self, tools: list[Tool], event: ProvidedToolCallEvent):
        tool: Tool | None = None
        for t in tools:
            if t.name == event.tool:
                tool = t


        text_result = f"tool '{event.tool}' is not exist"
        if isinstance(tool,Tool):
            try:
                text_result = tool.execute(event.args)
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
