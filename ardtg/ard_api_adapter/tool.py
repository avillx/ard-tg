from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.tool_results import resolve_tool_call
from ardtg.ard_api.models import Error, ToolResultPayload
from ardtg.ard_api_adapter.chat import prepare_content_part
from ardtg.domain.tool import ToolResultSink

if TYPE_CHECKING:
    import logging

    from ardtg.ard_api.client import Client
    from ardtg.domain.chat import ToolResult


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
    def send_result(self, res: ToolResult) -> None:

        cp = prepare_content_part(res.content)

        response = resolve_tool_call.sync(
            id=res.result_id,
            body=ToolResultPayload(result=cp),
            client=self._client,
        )

        if isinstance(response, Error):
            raise Exception(response.message)

        if response is None:
            raise Exception(f"unexpected agent response: result_id: {res.result_id}")
