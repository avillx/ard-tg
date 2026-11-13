import hmac
import json
import secrets
from email.message import Message
from typing import Any, override

import telebot
from telebot import types as telebot_types

import attach
import contacts
from server import http_server


class WebhookHandler(http_server.EndpointHandler):
    """
    Assuming for serve endpoint `/bot`
        Serve telegram Bot requests
    """

    _bot: telebot.TeleBot
    _secret_token: str

    def __init__(self, bot: telebot.TeleBot, webhook_url: str):
        super().__init__()
        self._secret_token = secrets.token_hex(32)
        self._bot = bot
        _ = bot.remove_webhook()
        _ = bot.set_webhook(
            url=webhook_url,
            secret_token=self._secret_token,
        )

    @override
    def handle(
        self,
        headers: "Message[str, str]",  # noqa
        body: bytes,
        response_sink: http_server.ResponseSink,
    ):

        # virefy header token
        if not hmac.compare_digest(
            headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            self._secret_token,
        ):
            response_sink.send_code(403)
            return

        try:
            update = telebot_types.Update.de_json(json.loads(body))
            if update is None:
                raise Exception("telegram send empty update")

            self._bot.process_new_updates([update])
            response_sink.send_code(200)
        except Exception:
            response_sink.send_code(500)
            return


class AttachSessionHandler(http_server.EndpointHandler):
    """
    Assuming for serve endpoint `/contacts`
    responses:
        - 200
        - 400 with failed validations explanation
    """

    _attach_service: attach.AttachService

    def __init__(self, attach_service: attach.AttachService):
        self._attach_service = attach_service

    @override
    def handle(
        self,
        headers: "Message[str, str]",  # noqa
        body: bytes,
        response_sink: http_server.ResponseSink,
    ):

        try:
            request: dict[str, Any] = json.loads(body)
        except Exception:
            response_sink.send_code(400)
            return

        # get values
        session_id = request.get("session_id")
        chat_id = request.get("chat_id")
        message = request.get("message")
        await_time = request.get("await_time")

        # validate values
        if not isinstance(session_id, str) or not session_id or session_id == "":
            response_sink.send_error(400, "bad session_id field")
            return

        if not isinstance(chat_id, int) or not chat_id:
            response_sink.send_error(400, "bad chat_id field")
            return

        if not isinstance(message, str) or not message:
            response_sink.send_error(400, "bad message field")
            return

        if not isinstance(await_time, int) or not int:
            response_sink.send_error(400, "bad await time field")
            return

        try:
            self._attach_service.attach(
                chat_id=chat_id,
                session_id=session_id,
                message=message,
                await_time=float(await_time),
            )
        except Exception as e:
            response_sink.send_error(400, f"attach {e}")
            return

        response_sink.send_code(200)


class ContactsHandler(http_server.EndpointHandler):
    """
    Assuming for serve endpoint `/contacts`
    responses:
        - 200 + json
        - 400
    """

    _contact_service: contacts.ContactService

    def __init__(self, contact_service: contacts.ContactService):
        super().__init__()
        self._contact_service = contact_service

    @override
    def handle(
        self,
        headers: "Message[str, str]",  # noqa
        body: bytes,
        response_sink: http_server.ResponseSink,
    ):
        try:
            contacts = self._contact_service.contacts()
            response_sink.send_json(200, {"contacts": contacts})
        except Exception:
            response_sink.send_code(400)


class HealthHandler(http_server.EndpointHandler):
    """
    Assuming for serve endpoint `/health`
    responses:
        - 200
    """

    @override
    def handle(
        self,
        headers: "Message[str, str]",  # noqa
        body: bytes,
        response_sink: http_server.ResponseSink,
    ):
        response_sink.send_code(200)
