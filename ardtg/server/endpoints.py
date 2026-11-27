import hmac
import json
import secrets
from typing import TYPE_CHECKING, Any, override

import telebot
from telebot import types as telebot_types

from ardtg.server.http_server import EndpointHandler, ErrorResponse, JSONResponse, Response

if TYPE_CHECKING:
    import logging
    from email.message import Message

    from ardtg.domain.attach import Attacher
    from ardtg.domain.contacts import ContactStore


class WebhookHandler(EndpointHandler):
    """Serve the `/bot` endpoint that receives Telegram bot requests."""

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
    def handle(self, headers: "Message[str, str]", body: bytes) -> Response:  # noqa

        # virefy header token
        if not hmac.compare_digest(
            headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            self._secret_token,
        ):
            return Response(403)

        try:
            json_dictionary = json.loads(body)  # pyright: ignore[reportAny]
            update = telebot_types.Update.de_json(json_dictionary)  # pyright: ignore[reportAny]
            if update is None:
                raise Exception("telegram send empty update")

            self._bot.process_new_updates([update])
            return Response(200)

        except Exception:  # noqa: BLE001 - any failure must answer 500
            return Response(500)


class AttachSessionHandler(EndpointHandler):
    """Serve the `/attach` endpoint

    responses:
        - 200
        - 400 with failed validations explanation
    """

    _attacher: Attacher

    def __init__(self, attacher: Attacher):
        self._attacher = attacher

    @override
    def handle(self, headers: "Message[str, str]", body: bytes) -> Response:  # noqa

        try:
            request: dict[str, Any] = json.loads(body)  # pyright: ignore[reportExplicitAny, reportAny]
        except Exception:  # noqa: BLE001 - any parse failure means bad request
            return Response(400)

        # get values
        session_id = request.get("session_id")
        chat_id = request.get("chat_id")
        message = request.get("message")
        await_time = request.get("await_time")

        # validate values
        if not isinstance(session_id, str) or not session_id or session_id == "":
            return ErrorResponse(400, "bad session_id field")

        if not isinstance(chat_id, int) or not chat_id:
            return ErrorResponse(400, "bad chat_id field")

        if not isinstance(message, str) or not message:
            return ErrorResponse(400, "bad message field")

        if not isinstance(await_time, int) or not int:
            return ErrorResponse(400, "bad await time field")

        try:
            self._attacher.attach(
                chat_id=chat_id,
                session_id=session_id,
                message=message,
                await_time=float(await_time),
            )
        except Exception as e:  # noqa: BLE001 - report the attach failure to the caller
            return ErrorResponse(400, f"attach {e}")

        return Response(200)


class ContactsHandler(EndpointHandler):
    """Serve the `/contacts` endpoint

    responses:
        - 200 + json
        - 400
    """

    _contact_storage: ContactStore
    _logger: logging.Logger

    def __init__(self, contact_storage: ContactStore, logger: logging.Logger):
        super().__init__()
        self._contact_storage = contact_storage
        self._logger = logger

    @override
    def handle(self, headers: "Message[str, str]", body: bytes) -> Response:  # noqa
        try:
            contacts = self._contact_storage.contacts()
            return JSONResponse(200, {"contacts": contacts})

        except Exception as err:  # noqa: BLE001 - storage backend is pluggable
            self._logger.error("problems with /contacts endpoint: %s", err)
            return Response(500)


class HealthHandler(EndpointHandler):
    """Serve the `/health` endpoint

    responses:
        - 200
    """

    @override
    def handle(self, headers: "Message[str, str]", body: bytes) -> Response:  # noqa
        return Response(200)
