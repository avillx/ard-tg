import api_bindings.arch_agent_api_client.api.tools.list_tools as list_tools
from api_bindings.arch_agent_api_client.models.content_part import ContentPart
import api_bindings.arch_agent_api_client.client as agent_client
import api_bindings.arch_agent_api_client.models as models
import httpx
import json
from typing import Callable
import tools
import logging as log


class AgentService:
    _agent_url :str
    _agent_id : str
    _agent_client : agent_client.Client

    def __init__(self, agent_url: str, agent_id : str, agent_client : agent_client.Client):
        self._agent_url = agent_url
        self._agent_id = agent_id
        self._agent_client = agent_client

    def tool_list(self) -> list[models.ToolServerInfo]:
        tool_servers_dto : models.ListToolsResponse200 =  list_tools.sync(client=self._agent_client)
        if tool_servers_dto is None:
            return None

        tool_servers_list: list[models.ToolServerInfo] = tool_servers_dto.tool_servers
        if tool_servers_list is None or len(tool_servers_list) <= 0:            
            return None

        return tool_servers_list
    
    def agent_request(
            self,
            request : str, 
            *,
            provided_tools : list[tools.AgentTool] = None,
            on_completion : Callable[[models.ChatCompletionMessage], None] = None,
            on_compaction : Callable[[models.ChatCompactionMessage], None] = None,
            on_error : Callable[[models.ChatErrorMessage], None] = None,
            on_tool_result : Callable[[models.ChatToolResultMessage], None] = None,
        ):

        tool_servers = []
        provided_tools_map : dict[str,Callable[[dict[str,any]],str]] = {}
        if provided_tools is not None:
            tool_servers.append(tools.create_provided_tool_server(provided_tools))

            for tool in provided_tools:
                provided_tools_map[tool.name()] = tool.execute

        chat_body : models.ChatBody = models.ChatBody(
            agent_id=self._agent_id,
            logging=True,
            session_id="e0edc0a6-608e-426f-9908-bb02e7129d29",
            user_request=[ContentPart(text=request)],
            tool_servers=tool_servers      
        )
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
            log.error(msg=f"agent_request: {e}")



def _run_chat_stream(
    agent_url: str,
    agent_client : agent_client.Client,
    chat_body : models.ChatBody,
    provided_tools_map: dict[str,Callable[[dict[str,any]],str]],
    on_completion : Callable[[models.ChatCompletionMessage], None] = None,
    on_compaction : Callable[[models.ChatCompactionMessage], None] = None,
    on_error : Callable[[models.ChatErrorMessage], None] = None,
    on_tool_result : Callable[[models.ChatToolResultMessage], None] = None,
):

    def on_provided_tool_call(call : models.ChatProvidedToolCallMessage):
        call_executor = provided_tools_map[call.payload.tool]
        if call_executor is None:
            return

        args : dict[str,any] = {}
        if call.payload.args is not None:
            args = call.payload.args

        tools.resolve_call(
            tool_executor=call_executor,
            client=agent_client,
            result_sink_id=call.payload.result_link,
            args=args,
        )
            
    with httpx.stream(
        "POST", 
        agent_url+"/chat", 
        json=chat_body.to_dict(), 
        timeout=9999,
    ) as response:
        for line in response.iter_lines():
            if line == "":
                continue

            response = determine_response(line)
            _process_response(
                response=response,
                on_provided_tool_call=on_provided_tool_call,
                on_compaction=on_compaction,
                on_completion=on_completion,
                on_error=on_error,
                on_tool_result=on_tool_result,
            )


def _process_response(
    response : 
        None |
        models.ChatProvidedToolCallMessage | 
        models.ChatCompactionMessage | 
        models.ChatCompletionMessage |
        models.ChatErrorMessage |
        models.ChatToolResultMessageType,
    on_provided_tool_call : Callable[[models.ChatProvidedToolCallMessage], None] = None,
    on_completion : Callable[[models.ChatCompletionMessage], None] = None,
    on_compaction : Callable[[models.ChatCompactionMessage], None] = None,
    on_error : Callable[[models.ChatErrorMessage], None] = None,
    on_tool_result : Callable[[models.ChatToolResultMessage], None] = None,
):
    match response :
        case None:
            return
        case models.ChatProvidedToolCallMessage():
            on_provided_tool_call(response)
        case models.ChatCompactionMessage():
            if on_compaction is not None:
                on_compaction(response)
        case models.ChatCompletionMessage():
            if on_completion is not None:
                on_completion(response)
        case models.ChatErrorMessage():
            if on_error is not None:
                on_error(response)                
        case models.ChatToolResultMessageType():
            if on_tool_result is not None:
                on_tool_result(response)

def determine_response(response : str) -> any:
    if "data: [DONE]" in response:
        return None
    
    try:
        completion_dict = json.loads(response.removeprefix("data: "))
        match completion_dict["type"]:
            case models.ChatCompletionMessageType.COMPLETE:
                return models.ChatCompletionMessage.from_dict(completion_dict)
            case models.ChatCompactionMessageType.COMPACTION:
                return models.ChatCompactionMessage.from_dict(completion_dict)
            case models.ChatErrorMessageType.ERROR:
                return models.ChatErrorMessage.from_dict(completion_dict)
            case models.ChatProvidedToolCallMessageType.PROVIDED_TOOLCALL:
                return models.ChatProvidedToolCallMessage.from_dict(completion_dict)
            case models.ChatToolResultMessageType.TOOL_RESULT:
                return models.ChatToolResultMessage.from_dict(completion_dict)
        raise("unknown result type " + completion_dict["type"])

    except Exception as e:
        log.error(e)
        log.error(response)

    return None