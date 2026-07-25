# Arch-Agent Telegram Gateway

Arch agent integration with Telegram:
- API generated with `openapi-python-client`
- Implements agent event stream handler
- Has `send_sticker` tool
- Session has limited lifetime, drops session on expiry

## Commands
- `/tools <tool_server>` - Return list of available tools servers. Also accept tool server names as args
  if args is non nil then fetch detailed list of tools in mentioned servers.
- `/activity` - Return recent agent activity log.
- `/ping` - Reply with "pong" message. Command for check bot.

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