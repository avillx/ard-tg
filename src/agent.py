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

        create_session_request = models.CreateSessionBody(instruction="")

        resp = create_session.sync(
            self._agent_id,
            client=self._agent_client,
            body=create_session_request,
        )
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
        task_list: list[models.TaskConfig] = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        return task_list.tasks

    def tool_list(self) -> list[models.ToolServerInfo]:
        tool_servers_dto: list[models.ToolServerInfo] = list_tools.sync(client=self._agent_client)
        if tool_servers_dto is None:
            return None

        return tool_servers_dto

    def today_activity(self) -> list[models.ActivityRecord]:
        request = models.GetActivityBody(
            agent=self._agent_id, from_=datetime.datetime.now(datetime.UTC)
        )

        response: list[models.ActivityRecord] = get_activity.sync(
            client=self._agent_client,
            body=request,
        )
        # TODO: chech err / none

        return response

    def consolidate(self, on_completion: Callable[[str], None] = None):
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
                    completion_event = models.CompletionEvent.from_dict(event_dict)
                    if on_completion is not None:
                        try:
                            on_completion(completion_event.completion)
                        except Exception as e:
                            log.error(f"on_completion consolidation process: {e}")
        except Exception as e:
            log.error(f"consolidation process: {e}")

    def agent_request(
        self,
        request: str,
        *,
        provided_tools: list[tools.AgentTool] = None,
        on_loop_exit: Callable[[models.LoopExitEvent], None] = None,
        on_completion: Callable[[models.CompletionEvent], None] = None,
        on_compltion_mistake: Callable[[models.CompletionMistakeEvent], None] = None,
        on_compaction: Callable[[models.CompactionEvent], None] = None,
        on_tool_result: Callable[[models.ToolResultEvent], None] = None,
        on_tool_error: Callable[[models.ToolErrorEvent], None] = None,
    ):

        tool_servers = []
        provided_tools_map: dict[str, Callable[[dict[str, any]], str]] = {}
        if provided_tools is not None:
            tool_servers.append(tools.create_provided_tool_server(provided_tools))

            for tool in provided_tools:
                provided_tools_map[tool.name()] = tool.execute

        session = self._session_service.get_actual_session()
        chat_body: models.ChatBody = models.ChatBody(
            logging=True,
            user_request=[ContentPart(text=request)],
            tool_servers=tool_servers,
        )
        log.debug(f"session: {session}")

        try:
            _run_chat_stream(
                agent_id=self._agent_id,
                session_id=session,
                agent_url=self._agent_url,
                agent_client=self._agent_client,
                chat_body=chat_body,
                provided_tools_map=provided_tools_map,
                on_loop_exit=on_loop_exit,
                on_completion=on_completion,
                on_compltion_mistake=on_compltion_mistake,
                on_compaction=on_compaction,
                on_tool_result=on_tool_result,
                on_tool_error=on_tool_error,
            )
        except Exception as e:
            interrupt_chat.sync(
                agent=self._agent_id,
                client=self._agent_client,
                session=session,
            )
            log.error(msg=f"agent request: {e}")


def _run_chat_stream(
    agent_url: str,
    agent_client: agent_client.Client,
    agent_id: str,
    session_id : str,
    chat_body: models.ChatBody,
    provided_tools_map: dict[str, Callable[[dict[str, any]], str]],
    on_loop_exit: Callable[[models.LoopExitEvent], None] = None,
    on_completion: Callable[[models.CompletionEvent], None] = None,
    on_compltion_mistake: Callable[[models.CompletionMistakeEvent], None] = None,
    on_compaction: Callable[[models.CompactionEvent], None] = None,
    on_tool_result: Callable[[models.ToolResultEvent], None] = None,
    on_tool_error: Callable[[models.ToolErrorEvent], None] = None,
):

    def on_provided_tool_call(call: models.ProvidedToolCallEvent):

        # process
        result = ""
        tool = call.tool
        try:
            call_executor = provided_tools_map[tool]

            args: dict[str, any] = {}
            if call.args is not None:
                args = call.args

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
            id=call.result_id,
        )

    with httpx.stream(
        "POST",
        agent_url + f"chat/{agent_id}/{session_id}",
        json=chat_body.to_dict(),
        timeout=10000,
    ) as response:
        for line in response.iter_lines():
            if line == "":
                continue

            _process_response(
                response=determine_response(line),
                on_provided_tool_call=on_provided_tool_call,
                on_loop_exit=on_loop_exit,
                on_completion=on_completion,
                on_compltion_mistake=on_compltion_mistake,
                on_compaction=on_compaction,
                on_tool_result=on_tool_result,
                on_tool_error=on_tool_error,
            )


def _process_response(
    response: None
    | models.LoopExitEvent
    | models.ProvidedToolCallEvent
    | models.CompactionEvent
    | models.CompletionEvent
    | models.CompletionMistakeEvent
    | models.ToolErrorEvent
    | models.ToolResultEvent,

    # callbacks
    on_loop_exit: Callable[[models.LoopExitEvent], None] = None,
    on_provided_tool_call: Callable[[models.ProvidedToolCallEvent], None] = None,
    on_completion: Callable[[models.CompletionEvent], None] = None,
    on_compltion_mistake: Callable[[models.CompletionMistakeEvent], None] = None,
    on_compaction: Callable[[models.CompactionEvent], None] = None,
    on_tool_result: Callable[[models.ToolResultEvent], None] = None,
    on_tool_error: Callable[[models.ToolErrorEvent], None] = None,
):
    match response:
        case None:
            return

        # provided call event
        case models.ProvidedToolCallEvent():
            on_provided_tool_call(response)

        # compactuion event
        case models.CompactionEvent():
            if on_compaction is not None:
                on_compaction(response)

        # compltion event
        case models.CompletionEvent():
            if on_completion is not None:
                on_completion(response)

        # completion mistake event
        case models.CompletionMistakeEvent():
            if on_compltion_mistake is not None:
                on_compltion_mistake(response)

        # exit loop event
        case models.LoopExitEvent():
            if on_loop_exit is not None:
                on_loop_exit(response)

        # tool result event
        case models.ToolResultEventType():
            if on_tool_result is not None:
                on_tool_result(response)

        # tool err event
        case models.ToolErrorEvent():
            if on_tool_error is not None:
                on_tool_error(response)


def determine_response(response: str) -> any:
    if "data: [DONE]" in response:
        return None

    try:
        event_dict = json.loads(response.removeprefix("data: "))
        match event_dict["type"]:

            # loop exit
            case "loop_exit":
                return models.LoopExitEvent.from_dict(event_dict)

            # completion
            case "complete":
                return models.CompletionEvent.from_dict(event_dict)

            # completion mistake
            case "complete_mistake":
                return models.CompletionMistakeEvent.from_dict(event_dict)

            # compaction
            case "compaction":
                return models.CompactionEvent.from_dict(event_dict)

            # tool error
            case "tool_error":
                return models.ToolErrorEventType.from_dict(event_dict)

            # provided tool call
            case "provided_toolcall":
                return models.ProvidedToolCallEvent.from_dict(event_dict)

            # tool result
            case "tool_result":
                return models.ToolResultEvent.from_dict(event_dict)

        raise f'unknown result type {event_dict["type"]}'

    except Exception as e:
        log.error(f"determine_response: bad response type: {e}")

    return None
