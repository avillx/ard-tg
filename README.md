# Arch-Agent Telegram Gateway

Arch agent integration with Telegram:
- API generated with `openapi-python-client`
- Implements agent event stream handler
- Has `send_sticker` tool
- Session has limited lifetime, drops session on expiry

Accepted env:
- `TELEGRAM_TOKEN` *required* - Telegram bot token
- `AGENT_URL` *required* - address of agent server
- `AGENT_ID` *required* - id of agent recipient
- `SESSION_LIFE_TIME` *required* - time in seconds before dropping session
- `STICKER_PACK` *optional* - name of sticker pack for agent usage
- `WEBHOOK_URL` *optional* - if not empty bot starts with webhook (port is `8443`)

Details:
- Agent has no `send_sticker` tool if sticker pack is not defined
- webhook has no ssl, for webhook you must use reverse proxy with ssl (nginx,traefic etc...)