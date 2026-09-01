import hmac
import json
import logging
import secrets
import sys
import threading
from abc import ABC, abstractmethod
from http.client import HTTPMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import telebot

import session


class ResponseSink:
    hanlder : BaseHTTPRequestHandler

    def __init__(self,hanlder : BaseHTTPRequestHandler):
        self.hanlder = hanlder

    def send_code(self,code : int):
        self.hanlder.send_response(code)
        self.hanlder.end_headers()


class EndpointHandler(ABC):
    @abstractmethod
    def handle(self, headers: HTTPMessage ,body: bytes, response_sink: ResponseSink):
        pass


class WebhookHandler(EndpointHandler):
    _bot : telebot.TeleBot
    _secret_token : str

    def __init__(self, bot: telebot.TeleBot, secret_token:str):
        super().__init__()
        self._bot = bot
        self._secret_token = secret_token

    def handle(self, headers: HTTPMessage, body: bytes, response_sink: ResponseSink):

        # virefy header token
        if not hmac.compare_digest(
            headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            self._secret_token,
        ):
            response_sink.send_code(403)
            return

        try:
            update = telebot.types.Update.de_json(json.loads(body))
            self._bot.process_new_updates([update])
            response_sink.send_code(200)
        except Exception:
            response_sink.send_code(400)
            return

class SessionSetHandler(EndpointHandler):
    _session_service: session.SessionService

    def __init__(self, session_service: session.SessionService):
        self._session_service = session_service

    def handle(self, headers: HTTPMessage, body: bytes, response_sink: ResponseSink):

        try:
            request : dict[str,str] = json.loads(body)
        except Exception:
            response_sink.send_code(400)
            return

        session_id = request.get("id")
        if not isinstance(session_id, str) or not session_id or session_id == "":
            response_sink.send_code(400)
            return

        self._session_service.set_session(session_id)
        response_sink.send_code(200)


def bot_webhook_handler(bot: telebot.TeleBot, url: str, webhook_path: str) -> WebhookHandler:
    secret_token = secrets.token_hex(32)

    bot.remove_webhook()
    bot.set_webhook(
        url=url+webhook_path,
        secret_token=secret_token,
    )

    return WebhookHandler(
        bot=bot,
        secret_token=secret_token,
    )

def build_server(post_routes: dict[str, EndpointHandler],logger: logging.Logger):

    class Server(BaseHTTPRequestHandler):

        def __init__(self, request, client_address, server):
            super().__init__(request, client_address, server)

        def do_POST(self):

            sink = ResponseSink(self)

            handler = post_routes.get(self.path)

            if not handler:
                sink.send_code(404)
                return

            if not isinstance(handler, EndpointHandler):
                sink.send_code(500)
                return

            length = int(self.headers.get("Content-Length", 0))

            handler.handle(
                headers=self.headers,
                body=self.rfile.read(length),
                response_sink=sink
            )

        def log_message(self, format, *args):
            logger.info(f"path {self.path} {format % args}")

    return ThreadingHTTPServer(("0.0.0.0", 8443), Server)

def serve_with_polling(bot: telebot.TeleBot, srv: ThreadingHTTPServer,logger: logging.Logger):
    def run_server():
        try:
            srv.serve_forever()
        except Exception as e:
            logger.error(f"serve {e}")
            sys.exit(1)

    threading.Thread(target=run_server, daemon=True).start()
    bot.infinity_polling(none_stop=True)
