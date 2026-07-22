# client : ArchAgentClient.Client = ArchAgentClient.Client(
#     base_url="http://localhost:9090/api/v1"
# )
import telebot
import telebot.formatting as fmt
import telebot.types as telebot_types
import os
from dotenv import load_dotenv
import api_bindings.arch_agent_api_client.client as client
import api_bindings.arch_agent_api_client.api.chat.chat as chat
import api_bindings.arch_agent_api_client.api.tools.list_tools as list_tools
from api_bindings.arch_agent_api_client.models.content_part import ContentPart

import api_bindings.arch_agent_api_client.models as models
import httpx
import json


load_dotenv()

_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
_AGENT_URL = os.getenv("AGENT_URL")

bot = telebot.TeleBot(_TELEGRAM_TOKEN,"MarkdownV2")
agent_client = client.Client(base_url=_AGENT_URL)


@bot.message_handler(commands=['tools'])
def send_welcome(message: telebot_types.Message):
    tool_servers_dto : models.ListToolsResponse200 =  list_tools.sync(client=agent_client)
    if tool_servers_dto is None:
        bot.send_message(message.chat.id,"Agent not responding")
        return

    tool_servers_list: list[models.ToolServerInfo] = tool_servers_dto.tool_servers
    if tool_servers_list is None or len(tool_servers_list) <= 0:
        bot.send_message(message.chat.id,"bad respond")
        return

    for tool_server in tool_servers_list: 
        servers_list = [fmt.mbold("🔧 "+fmt.escape_markdown(tool_server.name))] 

        server_tools :list[models.ToolInfo] = tool_server.tools
        if server_tools is None:
            continue

        for tool_info in server_tools:
            servers_list.append(fmt.format_text(
                    fmt.mbold("Tool: "+ fmt.escape_markdown(tool_info.name)) ,
                    fmt.escape_markdown(tool_info.description)
                ))
        
        repsonse = fmt.format_text(*servers_list,separator="\n\n")
        bot.send_message(message.chat.id,repsonse)


@bot.message_handler(func=lambda message: True)
def echo_message(message: telebot_types.Message):
    req : chat.ChatBody = chat.ChatBody(
        agent_id="alpha",
        logging=True,
        session_id="e0edc0a6-608e-426f-9908-bb02e7129d29",
        user_request=[
            ContentPart(text="# Avill:\n"+message.text)
        ],
    )

    response = httpx.request("POST", _AGENT_URL+"/chat", json=req.to_dict(), timeout=9999)
    for line in response.iter_lines():
        match res := determineResponse(line):
            case None:
                continue
            case models.ChatProvidedToolCallMessage():
                pass # ///  !!!!!!!!!!!!!!!
            case models.ChatCompletionMessage():
                completion : str  = res.payload.completion
                if completion is None or "":
                    continue
                for m in completion.split(sep="\n\n"):
                    bot.send_message(message.chat.id,fmt.escape_markdown(m))
            case models.ChatCompactionMessage():
                bot.send_message(message.chat.id,"⚠️ session compacted")
            case models.ChatErrorMessage():                
                bot.send_message(message.chat.id,"somting goes wrong: " + fmt.escape_markdown(res.payload.cause))

            # case models.ChatToolResultMessageType():

            
def determineResponse(response : str) -> any:
    if "data: [DONE]" in response:
        return None
    
    response = response.removeprefix("data: ")

    try:
        completion_dict = json.loads(response)
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
        print(e)

    return None

bot.infinity_polling()