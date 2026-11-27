import logging
from typing import override

import ard.models as models
from ard_adapter.chat import prepare_content_part
from domain.chat import ToolResult
from domain.tool import ToolResultSink
from ard.api.tool_results import resolve_tool_call
from ard.client import Client


class AgentAPIResultSink(ToolResultSink):
    _client: Client
    _logger: logging.Logger

    def __init__(
        self,
        client: Client,
        logger: logging.Logger,
    ) -> None:
        super().__init__()
        self._client = client
        self._logger = logger

    @override
    def send_result(self,res: ToolResult) -> None:

        cp = prepare_content_part(res.content)

        response = resolve_tool_call.sync(
            id=res.result_id,
            body=models.ToolResultPayload(result=cp),
            client=self._client,
        )

        if isinstance(response,models.Error):
            raise Exception(response.message)

        if response is None:
            raise Exception(f"unexpected agent response: result_id: {res.result_id}")
