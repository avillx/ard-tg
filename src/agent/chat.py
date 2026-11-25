lazy import logging

import agent.event as event
import agent.interruption as interruption
import agent.session as session
import agent.tool as tool
import ard.client as agent_client
import ard.models as models
from ard.models.content_part import ContentPart

_DEFAULT_CHAT_STREAM_TIMEOUT = 10000

class ChatService:
    _agent_url: str
    _agent_client: agent_client.Client
    _session_source: session.SessionSource
    _interruptor: interruption.Interruptor
    _logger: logging.Logger

    def __init__(
        self,
        agent_url: str,
        agent_client: agent_client.Client,
        session_source: session.SessionSource,
        interruptor: interruption.Interruptor,
        logger: logging.Logger,
    ):
        self._logger = logger.getChild("Agent")
        self._agent_url = agent_url
        self._agent_client = agent_client
        self._session_source = session_source
        self._interruptor = interruptor


    def _build_url(self) -> str:
        return "/".join(
            [
                self._agent_url.rstrip("/"),
                "chat",
                self._session_source.get_unexpired_session_id(),
            ]
        )

    def chat(
        self,
        request: str,
        *,
        event_handler: event.EventHandler,
        provided_tools: list[tool.Tool],
    ):
        """Run the agentic loop with the provided tools _DEFAULT_CHAT_STREAM_TIMEOUT
        All events are processed through the introduced event handler
        """

        chat_event_handler = event.ChatEventHandler(
            client=self._agent_client,
            event_handler=event_handler,
            provided_tools=provided_tools,
        )

        chat_body: models.ChatBody = models.ChatBody(
            logging=True,
            user_request=[ContentPart(text=request)],
            tool_servers=chat_event_handler.allowed_tool_servers(),
        )

        self._logger.info("Agentic loop requested")

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            url=self._build_url(),
            json=chat_body.to_dict(),
            timeout=_DEFAULT_CHAT_STREAM_TIMEOUT,
        ) as response:
            for line in response.iter_lines():
                self._process_line(chat_event_handler,line)

    def _process_line(self,event_handler: event.ChatEventHandler, line: str):
        if line == "":
            return

        try:
            ev = event.determine_response(line)
            if ev is None:
                return
        except Exception as e:  # noqa: BLE001 - malformed stream line
            self._logger.error("agent api: %s", e)
            return

        try:
            event_handler.process_event(ev)
        except Exception as e:  # noqa: BLE001 - event handlers are external code
            self._logger.error("chat declined cause: %s", e)
            self._interruptor.interrupt()
