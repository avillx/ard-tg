---
name: contact-user
description:
  Use this skill when the agent is running autonomously and needs to reach a human user — to report progress, ask a question. Autonomous output otherwise has no recipient. This skill sends a message to the user through the Telegram, so any reply the user sends back is routed to agent.
version: 1.0.0
author: Avillx
---

# Contact-user

Contacts the user in Telegram.
Use this skill if you need to contact the user while working autonomously.

## Usage

To contact the user, use this [script](./scripts/send_message.py),
it sends a message to the user.

- `chat_id` *required* — chat id the message will be sent to
- `message` *required* — message the user will receive
- `await_time` *required* — integer in seconds

Example:
```shell
python ./scripts/send_message.py --await_time 6000 --chat_id 000000 --message "hi! i found some problems on the server"
```

Use it only once and stop reasoning. When the user sends a reply, you wake up automatically.

## ChatID

The user's Telegram chat id.
If you don't know this id, you can use a separate [script](./scripts/contacts.py)
that returns a list of contacts.

It is strictly required. Without this id the gateway will just return an error, since it doesn't know
where to send your message.

Example:
```shell
python ./scripts/contacts.py
```

## Message

The message the user will receive.

Once the user contacts you back, you have the full current context, so there's no reason to
repeat your full explanation.

A brief reason is fine.
- `Hey, did you forget to pick up your delivery?`
- `It's time to pay for hosting, just a reminder`

Before sending any message, check whether it's the first message today,
since the first message of the day should contain a greeting.
- `Hello! I've got some problems with the ssh keys`
- `Good morning. I have bad news: today there's a snow outage`

## Await Time

Estimated time your message will remain relevant.
If you send "good morning" and the user answers in the evening, your message 
is no longer relevant.

After the user responds, you're back — the waiting time no longer matters.
No need to think as if your conversation time is limited; only the waiting
time for a response is limited, not the conversation time after a response.

If you send a message at night, the user may be asleep, so set a longer await time —
10+ hours — since the user may check your message later.

Prompt table:
| seconds | in hours  |
|:-------:|:----------|
|`6000`   | 1 hour    |
|`12000`  | 2 hours   |
|`30000`  | 5 hours   |
|`60000`  | 10 hours  |
|`72000`  | 12 hours  |

> You can check the current time in the last line of `agents.log`.

## Stop answering

Under "stop answering", do not mention reasoning anymore.
Just respond with an empty message and no tool calls.

NEVER call sleep-like or await-like commands. Interrupt yourself and stop reasoning.
When the user responds, you wake up automatically.

## Contact workflow
1. Get the user's chat id if you don't have one
2. Check the current time
3. Send the message
4. Stop answering
5. After user respond, read any suitable communication protocol