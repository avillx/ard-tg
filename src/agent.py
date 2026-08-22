import datetime
import json
import logging as log
import threading
import time
from collections.abc import Callable

import httpx

import arch_agent.api.activity.get_activity as get_activity
import arch_agent.api.chat.interrupt_chat as interrupt_chat
import arch_agent.api.mcp.list_mcp_servers as list_mcp_servers
import arch_agent.api.sessions.create_session as create_session
import arch_agent.api.tasks.list_tasks as list_tasks
import arch_agent.api.tool_results.resolve_tool_call as tool_result
import arch_agent.api.tools.list_tools as list_tools
import arch_agent.client as agent_client
import arch_agent.models as models
import tools
from arch_agent.models.content_part import ContentPart


class SessionService:
    _agent_id: str
    _agent_client: agent_client.Client
    _actual_session: str
    _last_update: float
    _life_time: float
    _mutex = threading.Lock()

    def __init__(self, agent_id: str, agent_client: agent_client.Client, life_time: float):
        self._agent_client = agent_client
        self._life_time = life_time
        self._agent_id = agent_id
        self._last_update = 0
        self._actual_session = ""
        self._mutex = threading.Lock()

    def get_current(self) -> str:
        with self._mutex:
            return self._actual_session

    def get_actual_session(self) -> str:
        with self._mutex:
            now = time.monotonic()

            # is expired
            if now - self._last_update > self._life_time:
                self._actual_session = self.create_new_session()
                self._last_update = now

            return self._actual_session

    def create_new_session(self) -> str:
        resp = create_session.sync(client=self._agent_client, agent=self._agent_id)
        if resp is None:
            log.error("agent return empty session")
            return ""
        return resp.id


class AgentService:
    _agent_url: str
    _agent_id: str
    _agent_client: agent_client.Client
    _session_service: SessionService

    def __init__(
        self,
        agent_url: str,
        agent_id: str,
        agent_client: agent_client.Client,
        session_service: SessionService,
    ):
        self._agent_url = agent_url
        self._agent_id = agent_id
        self._agent_client = agent_client
        self._session_service = session_service

    def interrupt(self):
        interrupt_chat.sync(
            agent=self._agent_id,
            session_id=self._session_service.get_current(),
            client=self._agent_client,
        )

    def mcp_list(self) -> list[models.MCPServerInfo]:
        mcp_servers = list_mcp_servers.sync(client=self._agent_client)
        if mcp_servers is None:
            return []

        return mcp_servers.mcp_servers

    def task_list(self) -> list[models.TaskConfig]:
        task_list: models.ListTasksResponse200 = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        return task_list.tasks

    def tool_list(self) -> list[models.ToolServerInfo]:
        tool_servers_dto: models.ListToolsResponse200 = list_tools.sync(client=self._agent_client)
        if tool_servers_dto is None:
            return None

        tool_servers_list: list[models.ToolServerInfo] = tool_servers_dto.tool_servers
        if tool_servers_list is None or len(tool_servers_list) <= 0:
            return None

        return tool_servers_list

    def today_activity(self) -> list[models.ActivityRecord]:
        request = models.GetActivityBody(
            agent=self._agent_id, from_=datetime.datetime.now(datetime.UTC)
        )

        response: models.ActivityLogsResponse = get_activity.sync(
            client=self._agent_client,
            body=request,
        )
        match response:
            case models.ActivityLogsResponse():
                activity: list[models.ActivityRecord] = response.activity
                if activity is not None:
                    return activity

        log.error(f"agent server return bad activity: {response}")
        return []

    def consolidate(self, on_completion: Callable[[models.ChatCompletionPayload], None] = None):
        try:
            with httpx.stream(
                method="POST",
                timeout=10000,
                url=self._agent_url + f"/memory/{self._agent_id}/consolidate",
            ) as response:
                for line in response.iter_lines():
                    if line == "" or "data: [DONE]" in line:
                        continue

                    event_dict = json.loads(line.removeprefix("data: "))
                    completion_event = models.ChatCompletionPayload.from_dict(event_dict)
                    if on_completion is not None:
                        try:
                            on_completion(completion_event)
                        except Exception as e:
                            log.error(f"on_completion consolidation process: {e}")
        except Exception as e:
            log.error(f"consolidation process: {e}")

    def agent_request(
        self,
        request: str,
        *,
        provided_tools: list[tools.AgentTool] = None,
        on_completion: Callable[[models.ChatCompletionEvent], None] = None,
        on_compaction: Callable[[models.ChatCompactionEvent], None] = None,
        on_error: Callable[[models.ChatErrorEvent], None] = None,
        on_tool_result: Callable[[models.ChatToolResultEvent], None] = None,
    ):

        tool_servers = []
        provided_tools_map: dict[str, Callable[[dict[str, any]], str]] = {}
        if provided_tools is not None:
            tool_servers.append(tools.create_provided_tool_server(provided_tools))

            for tool in provided_tools:
                provided_tools_map[tool.name()] = tool.execute

        session = self._session_service.get_actual_session()
        chat_body: models.ChatBody = models.ChatBody(
            agent_id=self._agent_id,
            logging=True,
            session_id=session,
            user_request=[ContentPart(text=request)],
            tool_servers=tool_servers,
        )
        log.debug(f"session: {session}")

        try:
            _run_chat_stream(
                agent_url=self._agent_url,
                agent_client=self._agent_client,
                chat_body=chat_body,
                provided_tools_map=provided_tools_map,
                on_completion=on_completion,
                on_compaction=on_compaction,
                on_error=on_error,
                on_tool_result=on_tool_result,
            )
        except Exception as e:
            interrupt_chat.sync(
                agent=self._agent_id,
                client=self._agent_client,
                session_id=session,
            )
            log.error(msg=f"agent_request: {e}")


def _run_chat_stream(
    agent_url: str,
    agent_client: agent_client.Client,
    chat_body: models.ChatBody,
    provided_tools_map: dict[str, Callable[[dict[str, any]], str]],
    on_completion: Callable[[models.ChatCompletionEvent], None] = None,
    on_compaction: Callable[[models.ChatCompactionEvent], None] = None,
    on_error: Callable[[models.ChatErrorEvent], None] = None,
    on_tool_result: Callable[[models.ChatToolResultEvent], None] = None,
):

    def on_provided_tool_call(call: models.ChatProvidedToolCallEvent):

        # process
        result = ""
        tool = call.payload.tool
        try:
            call_executor = provided_tools_map[tool]

            args: dict[str, any] = {}
            if call.payload.args is not None:
                args = call.payload.args

            result = call_executor(args)

        except KeyError:
            result = f"tool '{tool}' is not exist"
        except Exception:
            result = "errors in tool precessing"

        # respond
        answer = models.ToolResultPayload(result=[models.ContentPart(text=result)])

        tool_result.sync(
            client=agent_client,
            body=answer,
            id=call.payload.result_id,
        )

    with httpx.stream(
        "POST",
        agent_url + "/chat",
        json=chat_body.to_dict(),
        timeout=10000,
    ) as response:
        for line in response.iter_lines():
            if line == "":
                continue

            _process_response(
                response=determine_response(line),
                on_provided_tool_call=on_provided_tool_call,
                on_compaction=on_compaction,
                on_completion=on_completion,
                on_error=on_error,
                on_tool_result=on_tool_result,
            )


def _process_response(
    response: None
    | models.ChatProvidedToolCallEvent
    | models.ChatCompactionEvent
    | models.ChatCompletionEvent
    | models.ChatErrorEvent
    | models.ChatToolResultEventType,
    on_provided_tool_call: Callable[[models.ChatProvidedToolCallEvent], None] = None,
    on_completion: Callable[[models.ChatCompletionEvent], None] = None,
    on_compaction: Callable[[models.ChatCompactionEvent], None] = None,
    on_error: Callable[[models.ChatErrorEvent], None] = None,
    on_tool_result: Callable[[models.ChatToolResultEvent], None] = None,
):
    match response:
        case None:
            return
        case models.ChatProvidedToolCallEvent():
            on_provided_tool_call(response)
        case models.ChatCompactionEvent():
            if on_compaction is not None:
                on_compaction(response)
        case models.ChatCompletionEvent():
            if on_completion is not None:
                on_completion(response)
        case models.ChatErrorEvent():
            if on_error is not None:
                on_error(response)
        case models.ChatToolResultEventType():
            if on_tool_result is not None:
                on_tool_result(response)


def determine_response(response: str) -> any:
    if "data: [DONE]" in response:
        return None

    try:
        event_dict = json.loads(response.removeprefix("data: "))
        match event_dict["type"]:
            case models.ChatCompletionEventType.COMPLETE:
                return models.ChatCompletionEvent.from_dict(event_dict)
            case models.ChatCompactionEventType.COMPACTION:
                return models.ChatCompactionEvent.from_dict(event_dict)
            case models.ChatErrorEventType.ERROR:
                return models.ChatErrorEvent.from_dict(event_dict)
            case models.ChatProvidedToolCallEventType.PROVIDED_TOOLCALL:
                return models.ChatProvidedToolCallEvent.from_dict(event_dict)
            case models.ChatToolResultEventType.TOOL_RESULT:
                return models.ChatToolResultEvent.from_dict(event_dict)
        raise ("unknown result type " + event_dict["type"])

    except Exception as e:
        log.error(f"determine_response: bad response type: {e}")

    return None
