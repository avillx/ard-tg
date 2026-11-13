import hmac
import json
import logging
import secrets
import signal
import threading
import types
from abc import ABC, abstractmethod
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, override

import telebot
from telebot import TeleBot
from telebot import types as telebot_types

import attach
import contacts
import notifications


class ResponseSink:
    hanlder: BaseHTTPRequestHandler

    def __init__(self, hanlder: BaseHTTPRequestHandler):
        self.hanlder = hanlder

    def send_code(self, code: int):
        self.hanlder.send_response(code)
        self.hanlder.end_headers()

    def send_error(self, code: int, explain: str):
        self.hanlder.send_error(code=code, explain=explain)
        self.hanlder.end_headers()

    def send_json(self, code: int, data: Any):

        response_body = json.dumps(data).encode("utf-8")

        self.hanlder.send_response(code)
        self.hanlder.send_header("Content-type", "application/json")
        self.hanlder.send_header("Content-Length", str(len(response_body)))
        self.hanlder.end_headers()

        self.hanlder.wfile.write(response_body)


class EndpointHandler(ABC):
    @abstractmethod
    def handle(self, headers: "Message[str, str]", body: bytes, response_sink: ResponseSink):  # noqa
        pass


class WebhookHandler(EndpointHandler):
    _bot: telebot.TeleBot
    _secret_token: str

    def __init__(self, bot: telebot.TeleBot, secret_token: str):
        super().__init__()
        self._bot = bot
        self._secret_token = secret_token

    @override
    def handle(self, headers: "Message[str, str]", body: bytes, response_sink: ResponseSink):  # noqa

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


class AttachSessionHandler(EndpointHandler):
    _attach_service: attach.AttachService

    def __init__(self, attach_service: attach.AttachService):
        self._attach_service = attach_service

    @override
    def handle(self, headers: "Message[str, str]", body: bytes, response_sink: ResponseSink):  # noqa

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


class ContactsHandler(EndpointHandler):
    _contact_service: contacts.ContactService

    def __init__(self, contact_service: contacts.ContactService):
        super().__init__()
        self._contact_service = contact_service

    @override
    def handle(self, headers: "Message[str, str]", body: bytes, response_sink: ResponseSink):  # noqa
        try:
            contacts = self._contact_service.contacts()
            response_sink.send_json(200, {"contacts": contacts})
        except Exception:
            response_sink.send_code(400)


class HealthHandler(EndpointHandler):
    @override
    def handle(self, headers: "Message[str, str]", body: bytes, response_sink: ResponseSink):  # noqa
        response_sink.send_code(200)


def bot_webhook_handler(bot: telebot.TeleBot, url: str, webhook_path: str) -> WebhookHandler:
    secret_token = secrets.token_hex(32)

    _ = bot.remove_webhook()
    _ = bot.set_webhook(
        url=url + webhook_path,
        secret_token=secret_token,
    )

    return WebhookHandler(
        bot=bot,
        secret_token=secret_token,
    )


def build_server(
    *,
    post_routes: dict[str, EndpointHandler],
    get_routes: dict[str, EndpointHandler],
    logger: logging.Logger,
):

    logger = logger.getChild("Server")

    class Server(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            super().__init__(request, client_address, server)

        def do_GET(self):
            sink = ResponseSink(self)

            handler = get_routes.get(self.path)
            if not handler:
                sink.send_code(404)
                return

            length = int(self.headers.get("Content-Length", 0))

            handler.handle(headers=self.headers, body=self.rfile.read(length), response_sink=sink)

        def do_POST(self):

            sink = ResponseSink(self)

            handler = post_routes.get(self.path)
            if not handler:
                sink.send_code(404)
                return

            length = int(self.headers.get("Content-Length", 0))

            handler.handle(headers=self.headers, body=self.rfile.read(length), response_sink=sink)

        @override
        def log_message(self, format, *args):
            logger.info(f"{format % args}")

    return ThreadingHTTPServer(("0.0.0.0", 8443), Server)


class BotServer:
    _bot: TeleBot
    _httpServer: ThreadingHTTPServer
    _logger: logging.Logger
    _notifier: notifications.Notifier
    _use_webhook: bool

    def __init__(
        self,
        logger: logging.Logger,
        attachment_service: attach.AttachService,
        contact_service: contacts.ContactService,
        notifier: notifications.Notifier,
        webhook_url: str,
    ) -> None:
        self._use_webhook = False

        post_routes: dict[str, EndpointHandler] = {
            "/attach": AttachSessionHandler(attachment_service)
        }

        get_routes: dict[str, EndpointHandler] = {
            "/contacts": ContactsHandler(contact_service),
            "/health": HealthHandler(),
        }

        if webhook_url != "":
            webhook_path = f"/bot/{secrets.token_hex(16)}"
            post_routes[webhook_path] = bot_webhook_handler(self._bot, webhook_url, webhook_path)
            self._use_webhook = True

        self._httpServer = build_server(
            get_routes=get_routes,
            post_routes=post_routes,
            logger=logger,
        )

    def run(self):

        notified: bool = False

        def notify_about_down():
            nonlocal notified
            if notified:
                return
            notified = True
            self._notifier.notify_about_down()

        ## Calls when server is take sigterm
        def _on_terminate(_signum: int, _frame: types.FrameType | None):
            self._logger.info("got SIGTERM, shutting down")
            notify_about_down()
            raise SystemExit(0)

        _ = signal.signal(signal.SIGTERM, _on_terminate)

        try:
            self._notifier.notify_about_up()

            ## Run with infinity polling
            if self._use_webhook is None:
                self._logger.info("run with polling")
                threading.Thread(target=self._httpServer.serve_forever, daemon=True).start()
                self._bot.infinity_polling(none_stop=True)

            ## Run with only webhook
            else:
                self._logger.info("run with webhook")
                self._httpServer.serve_forever()
        finally:
            notify_about_down()
