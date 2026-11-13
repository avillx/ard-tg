# Agent Runtime Daemon Telegram

![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pydantic](https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-%232CA5E0.svg?style=for-the-badge&logo=telegram&logoColor=white)

Telegram Gateway for [Agent Runtime Daemon](https://github.com/avillx/ard).

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

- `/interrupt` Interrupt agentic loop
- `/new` Starts a new session
- `/activity` Return recent agent activity log.
- `/tasks` Fetch message representation of taskm, per one agent scheduled task. With no request
- `/tools` Fetch list of available tools servers
- `/mcp` Fetch list of mcp servers with transport type (process/http)
- `/consolidate` immidiate starts memory consolidation, stream colsolidatior completions as messages


## Tools

Agent recieve additional tools for telegram. 
- `send_photo` agent can send photo in current chat by absolute path to file.
- `send_document` agent can attach file to current chat as a document. 
- `send_voice` agent can send file as a voice message (`.ogg`, `.mp3`).
- `send_sticker` agent can use telegram stickers in chats. 
  To enable feature add telegram sticker pack name in `ARDTG_STICKER_PACK` variable. 
  Agent has no `send_sticker` tool if sticker pack is not defined.


## Skills

Special skill for _ARD_ for this gateway
- [contact user](skills/ard-tg-contact-user) the agent can contact you outside of autonomous 
  operation and initiate messaging first.


## Files

Gateway keeps its files in two folders, each one is set by its own environment variable.

Gateway storage folder specifies via `ARDTG_FILESTORAGE_PATH` variable:
- `contacts.json` stores user contacts (all users whenever sent message to agent add to contacts)

Agent data folder specifies via `ARDTG_AGENT_DATAPATH` variable. It must match the agent
  working directory, because the gateway passes relative `tmp/...` paths to the agent:
- `tmp/` folder for files that was sent by user to agent
  (photos, audio, video, video notes, documents, voice messages, etc...)
  All messages sent to agent goes to this path, path to saved file passed to agent in message text.
- `skills/` folder with skills of this gateway, copied here on startup so the agent can use them


## Configuration

All configs provides via this envirement variables:
- `ARDTG_TELEGRAM_TOKEN` *required* - Telegram bot token
- `ARDTG_AGENT_URL` *required* - address of agent server
- `ARDTG_AGENT_DATAPATH` *required* - path to agent folder for store message attachments
  (videos, photos, voice, docs, etc...) and gateway skills, must match the agent working directory
- `ARDTG_FILESTORAGE_PATH` *required* - path to folder for store gateway files (`contacts.json`)
- `ARDTG_AGENT_ID` *optional* - id of agent recipient. `default - default`
- `ARDTG_SESSION_LIFE_TIME` *optional* - time in seconds before dropping session. `default - 600 (10min)`
- `ARDTG_STICKER_PACK` *optional* - name of sticker pack for agent usage
  Agent has no `send_sticker` tool if sticker pack is not defined
- `ARDTG_WEBHOOK_URL` *optional* - if not empty bot starts with webhook (port is `8443`)
  webhook has no ssl, for webhook you must use reverse proxy with ssl (nginx,traefic etc...)
- `ARDTG_ALLOWED_CHATS` *optional* - if not empty, updates works only on allowed chats (whitelist-like)
  is a telegram chat ids enumirated via comma (e.g `ARDTG_ALLOWED_CHATS=666666,777777` )
- `ARDTG_NOTIFY_CHAT_ID` *optional* - chat id that receives bot start and shutdown notifications
  Notifications are disabled if not set


## Set session

Current agent session can be set from external source
Also it sends notify message in selected chat

`POST /attach` accept json with fields:
- `session_id` *required* agent session id
- `chat_id` *required* user chat id
- `message` *required* message from agent to user
- `await_time` *required* additional time for await user answer

Return:
- `200` on success
- `400` on invalid json

Example:
```json
{
  "session_id" : "xxxxx-xxxxx-xxxxx-xxxxx",
  "chat_id" : 0000000,
  "message" : "Hi!",
  "await_time" : 6000
}
```


## Contacts

All users whenever sent message to agents add to contacts
Contacts stores in `contacts.json` in selected storage path
It can be taken by `GET /contacts` endpoint

Return:
- `200` on success
- `500` if something goes wrong


## Agent API

API generated with `openapi-python-client` from this [Specification](./agent-api.yml)


## Stack

- Python
- httpx
- pytelegrambotapi
- Pydantic


## License

This program is licensed under the GNU General Public License v3.0 (GPLv3). See the full license: `https://www.gnu.org/licenses/gpl-3.0.txt`

Source: `https://github.com/avillx/ard-tg`

```
avillx/ard-tg: Copyright (C) 2026 avillx

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```
