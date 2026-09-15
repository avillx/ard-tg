import datetime
import json
import logging
from collections.abc import Callable

import httpx

import agent.event as event
import agent.session as session
import agent.tool as tool
import arch_agent.api.activity.get_activity as get_activity
import arch_agent.api.chat.interrupt_chat as interrupt_chat
import arch_agent.api.mcp.list_mcp_servers as list_mcp_servers
import arch_agent.api.tasks.list_tasks as list_tasks
import arch_agent.api.tools.list_tools as list_tools
import arch_agent.client as agent_client
import arch_agent.models as models
from arch_agent.models.content_part import ContentPart

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
        """
        Sends to agent signal to interrupt actual session
        """
        session_id = self._session_service.get()
        self._logger.info(f"interrupting agent {self._agent_id}, session: {session_id}")

        interrupt_chat.sync_detailed(
            agent=self._agent_id,
            session=session_id,
            client=self._agent_client,
        )

    def mcp_list(self) -> dict[str, models.MCPServerInfo]:
        """
        Return list of records of mcp servers in agent system
        """
        self._logger.info("MCP servers requested")

        mcp_servers = list_mcp_servers.sync(client=self._agent_client)
        if mcp_servers is None:
            return {}

        return mcp_servers.to_dict()

    def task_list(self) -> list[models.TaskConfig]:
        """
        Return list of actual tasks in agent system
        """
        self._logger.info("Tasks requested")

        task_list = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        return task_list

    def tool_list(self) -> dict[str, models.ToolRepr]:
        """
        Return list of all working ToolServers

        dict key is a name of tool server
        dict
        """
        self._logger.info("Tools requested")

        tool_servers_dto = list_tools.sync(client=self._agent_client)
        if tool_servers_dto is None:
            return {}

        return tool_servers_dto.to_dict()

    def today_activity(self) -> list[models.ActivityRecord]:
        """
        Return note of today agent activity

        raise on errors abd bad validations
        """
        self._logger.info("Activity requested")
        request = models.GetActivityBody(
            agent=self._agent_id, from_=datetime.datetime.now(datetime.UTC)
        )

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

        return resp

    def consolidate(self, on_completion: Callable[[str], None]):
        """
        Starts immidiate agent memeory consolidation, all completions flush in
        a on_completion callback
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

        try:
            with httpx.stream(
                method="POST",
                timeout=10000,
                url=url,
            ) as response:
                for line in response.iter_lines():
                    if line == "" or "data: [DONE]" in line:
                        continue

                    event_dict = json.loads(line.removeprefix("data: "))
                    completion_event = models.CompletionEvent.from_dict(event_dict)

                    try:
                        on_completion(completion_event.completion)
                    except Exception as e:
                        self._logger.error(f"consolidation process: {e}")

        except Exception as e:
            self._logger.error(f"consolidation interrupted with exception: {e}")

    def agent_request(
        self,
        request: str,
        *,
        event_handler: event.EventHandler,
        provided_tools: list[tool.SafeTool],
    ):
        """
        Starts agentic loop with provided tools. all evetns was processed trough
        intruduced event handler
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

        self._logger.info(f"Agentic loop requested, session: {session_id}")

        # run request
        try:
            with httpx.stream(
                method="POST",
                url=url,
                json=chat_body.to_dict(),
                timeout=_DEFAULT_STREAM_TIMEOUT,
            ) as response:
                for line in response.iter_lines():
                    if line == "":
                        continue

                    ev = event.determine_response(line)
                    if ev is None:
                        # TODO: fix placeholder
                        return

                    agent_event_handler.process_event(ev)

        except Exception as e:
            self._logger.error(f"chat declined cause: {e}")
            self.interrupt()
