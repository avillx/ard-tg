from typing import TYPE_CHECKING, override

from ardtg.ard_api_adapter.chat import StopStream, determine_internal_response
from ardtg.domain.consolidation import ConsolidationStreamer

if TYPE_CHECKING:
    from ardtg.ard_api import Client

_DEFAULT_CONSOLIDATION_STREAM_TIMEOUT = 10000

class AgentAPIConsolidationAdapter(ConsolidationStreamer):
    _agent_client: Client
    _agent_url: str

    def __init__(
        self,
        client: Client,
        agent_url: str,
    ) -> None:
        self._agent_client = client
        self._agent_url = agent_url


    def _endpoint(self) -> str:
        return "/".join(
            [
                self._agent_url.rstrip("/"),
                "memory",
                "consolidate",
            ]
        )

    @override
    def consolidate(self):
        """Start agent memory consolidation immediately

        Completions are flushed into the on_completion callback
        """

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            timeout=_DEFAULT_CONSOLIDATION_STREAM_TIMEOUT,
            url=self._endpoint(),
        ) as response:
            for line in response.iter_lines():
                # keepalive strings is empty
                if line == "":
                    continue
                ev = determine_internal_response(line)
                if isinstance(ev,StopStream):
                    return
                yield ev
