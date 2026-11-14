import datetime as dt
import json
lazy import logging
lazy from collections.abc import Callable

import agent.event as event
import agent.session as session
import agent.tool as tool
import ard.api.activity.get_activity as get_activity
import ard.api.chat.interrupt_chat as interrupt_chat
import ard.api.mcp.list_mcp_servers as list_mcp_servers
import ard.api.tasks.list_tasks as list_tasks
import ard.api.tools.list_tools as list_tools
import ard.client as agent_client
import ard.models as models
from ard.models.content_part import ContentPart

_DEFAULT_STREAM_TIMEOUT = 10000


class Service:
    _agent_url: str
    _agent_id: str
    _agent_client: agent_client.Client
    _session_service: session.SessionService
    _logger: logging.Logger

    def __init__(
        self,
        agent_url: str,
        agent_id: str,
        agent_client: agent_client.Client,
        session_service: session.SessionService,
        logger: logging.Logger,
    ):
        self._logger = logger.getChild("Agent")
        self._agent_url = agent_url
        self._agent_id = agent_id
        self._agent_client = agent_client
        self._session_service = session_service

    def interrupt(self):
        """Interrupt the agent session in progress."""
        session_id = self._session_service.get()
        self._logger.info("interrupting agent %s, session: %s", self._agent_id, session_id)

        _ = interrupt_chat.sync_detailed(
            agent=self._agent_id,
            session=session_id,
            client=self._agent_client,
        )

    def mcp_list(self) -> dict[str, models.MCPServerInfo]:
        """Return the MCP servers known to the agent."""
        self._logger.info("MCP servers requested")

        mcp_servers = list_mcp_servers.sync(client=self._agent_client)
        if mcp_servers is None:
            return {}

        return mcp_servers.to_dict()

    def task_list(self) -> list[models.TaskConfig]:
        """Return the tasks configured in the agent."""
        self._logger.info("Tasks requested")

        task_list = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        return task_list

    def tool_list(self) -> dict[str, models.ToolRepr]:
        """Return all working tool servers

        dict key is a name of tool server
        dict
        """
        self._logger.info("Tools requested")

        tool_servers_dto = list_tools.sync(client=self._agent_client)
        if tool_servers_dto is None:
            return {}

        return tool_servers_dto.to_dict()

    def today_activity(self) -> list[models.ActivityRecord]:
        """Return today's agent activity

        raise on errors abd bad validations
        """
        self._logger.info("Activity requested")
        request = models.GetActivityBody(agent=self._agent_id, from_=dt.datetime.now(dt.UTC))

        resp = get_activity.sync(
            client=self._agent_client,
            body=request,
        )

        match resp:
            case None:
                return []

            case models.ValidationError():
                raise Exception(f"invalid request,{resp.to_dict()}")

            case models.Error():
                raise Exception(f"problem: {resp.message}")

            case _:
                pass

        return resp

    def consolidate(self, on_completion: Callable[[str], None]):
        """Start agent memory consolidation immediately

        Completions are flushed into the on_completion callback
        """
        self._logger.info("Consolidation requested")

        # assemble url adress
        url = "/".join(
            [
                self._agent_url.rstrip("/"),
                "memory",
                self._agent_id,
                "consolidate",
            ]
        )

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            timeout=10000,
            url=url,
        ) as response:
            for line in response.iter_lines():
                if line == "" or "data: [DONE]" in line:
                    continue

                try:
                    event_dict = json.loads(line.removeprefix("data: "))  # pyright: ignore[reportAny]
                    completion_event = models.CompletionEvent.from_dict(event_dict)  # pyright: ignore[reportAny]
                except Exception as e:  # noqa: BLE001 - malformed stream line
                    self._logger.error("consolidation: api respond bad json: %s", e)
                    continue

                try:
                    on_completion(completion_event.completion)
                except Exception as e:  # noqa: BLE001 - callback is external code
                    self._logger.error("consolidation process: %s", e)

    def agent_request(
        self,
        request: str,
        *,
        event_handler: event.EventHandler,
        provided_tools: list[tool.SafeTool],
    ):
        """Run the agentic loop with the provided tools

        All events are processed through the introduced event handler
        """
        session_id = self._session_service.get_actual()

        agent_event_handler = event.AgentEventHandler(
            client=self._agent_client,
            event_handler=event_handler,
            provided_tools=provided_tools,
        )

        chat_body: models.ChatBody = models.ChatBody(
            logging=True,
            user_request=[ContentPart(text=request)],
            tool_servers=agent_event_handler.allowed_tool_servers(),
        )

        # build URL
        url = "/".join(
            [
                self._agent_url.rstrip("/"),
                "chat",
                self._agent_id,
                session_id,
            ]
        )

        self._logger.info("Agentic loop requested, session: %s", session_id)

        httpx_client = self._agent_client.get_httpx_client()

        with httpx_client.stream(
            method="POST",
            url=url,
            json=chat_body.to_dict(),
            timeout=_DEFAULT_STREAM_TIMEOUT,
        ) as response:
            for line in response.iter_lines():
                if line == "":
                    continue

                try:
                    ev = event.determine_response(line)
                    if ev is None:
                        continue
                except Exception as e:  # noqa: BLE001 - malformed stream line
                    self._logger.error("agent api, session %s: %s", session_id, e)
                    continue

                try:
                    agent_event_handler.process_event(ev)
                except Exception as e:  # noqa: BLE001 - event handlers are external code
                    self._logger.error("chat declined cause: %s", e)
                    self.interrupt()
