# Arch-Agent Telegram Gateway

Gateway for arch-agent integration with Telegram.

It is intended as an additional channel, not a primary one, for contacting the agent when other
  channels are unavailable or inconvenient.
This means the gateway will never provide all agent capabilities, since a messenger interface
  is not convenient for co-working, coding, etc.

> Session has limited lifetime, drops session on expiry.

## Messages
All messages sended to bot will directed to agent, agent responses returned as bot messages. 
Bot has `typing...` status while agent processing request. 
Can be interrupted by command.

## Commands
- `/tools <tool_server>` - with no aguments - Return list of available tools servers. 
  Also accept tool server names as args when args is non nil - fetch detailed list of tools in mentioned servers.
- `/activity` - Return recent agent activity log.
- `/ping` - Reply with "pong" message. Command for check bot.
- `/tasks` - Fetch message representation of taskm, per one agent scheduled task. With no request
- `/mcp` - Fetch list of mcp servers with transport type (process/http)
- `/interrupt` - interrupt agentic loop
- `/consolidate` - immidiate starts memory consolidation

## Tools
Agent recieve additional tools for telegram. 
- `send_sticker` agent can use telegram stickers in chats. 
  To enable feature add telegram sticker pack name in `STICKER_PACK` variable.

## Configuration
All configs provides via this envirement variables:
- `TELEGRAM_TOKEN` *required* - Telegram bot token
- `AGENT_URL` *required* - address of agent server
- `AGENT_ID` *required* - id of agent recipient
- `SESSION_LIFE_TIME` *optional* - time in seconds before dropping session. `default - 600 (10min)`
- `STICKER_PACK` *optional* - name of sticker pack for agent usage
  Agent has no `send_sticker` tool if sticker pack is not defined
- `WEBHOOK_URL` *optional* - if not empty bot starts with webhook (port is `8443`)
  webhook has no ssl, for webhook you must use reverse proxy with ssl (nginx,traefic etc...)
- `ALLOWED_CHATS` *optional* - if not empty, updates works only on allowed chats (whitelist-like)
  is a telegram chat ids enumirated via comma (e.g `ALLOWED_CHATS=666666,777777` )

## Stack
- Python
- httpx
- pytelegrambotapi
- API generated with `openapi-python-client`