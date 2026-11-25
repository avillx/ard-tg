import json
from abc import ABC, abstractmethod
lazy import logging

import ard.client as agent_client
import ard.models as models
from agent.event import EventType, determine_response

_DEFAULT_CONSOLIDATION_STREAM_TIMEOUT = 10000


class ConsolidationEventHandler(ABC):
    def __init__(self) -> None:
        super().__init__()

    def process_event(self, event: EventType| None):
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

class ConsolidateService:
    _logger: logging.Logger
    _agent_client: agent_client.Client
    _agent_url: str
    _event_handler: ConsolidationEventHandler

    def __init__(
        self,
        client: agent_client.Client,
        agent_url: str,
        event_handler: ConsolidationEventHandler,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client
        self._agent_url = agent_url
        self._event_handler = event_handler


    def _endpoint(self) -> str:
        return "/".join(
            [
                self._agent_url.rstrip("/"),
                "memory",
                "consolidate",
            ]
        )


    def consolidate(self):
        """Start agent memory consolidation immediately

        Completions are flushed into the on_completion callback
        """
        self._logger.info("Consolidation requested")

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            timeout=_DEFAULT_CONSOLIDATION_STREAM_TIMEOUT,
            url=self._endpoint(),
        ) as response:
            for line in response.iter_lines():
                self._process_line(line)


    def _process_line(self,line: str) -> None:
        try:
            event_dict = json.loads(line.removeprefix("data: "))  # pyright: ignore[reportAny]
            completion_event = determine_response(event_dict)  # pyright: ignore[reportAny]
        except Exception as e:  # noqa: BLE001 - malformed stream line
            self._logger.error("consolidation: api respond bad json: %s", e)
            return

        try:
            self._event_handler.process_event(completion_event)
        except Exception as e:  # noqa: BLE001 - callback is external code
            self._logger.error("consolidation process: %s", e)
