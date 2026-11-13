import json
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, override
lazy import logging
lazy from email.message import Message

# The bot must accept webhook and attach calls from outside, so listen on every interface.
_SERVER_HOST = "0.0.0.0"  # noqa: S104
_SERVER_PORT = 8443


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


class Server:
    _logger: logging.Logger
    _get_routes: dict[str, EndpointHandler]
    _post_routes: dict[str, EndpointHandler]
    _stdlib_server: ThreadingHTTPServer

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("http_server")
        self._get_routes = {}
        self._post_routes = {}
        self._stdlib_server = self._build_ugly_stdlib_server()

    def get(self, endpoint: str, handler: EndpointHandler):
        self._get_routes[endpoint] = handler

    def post(self, endpoint: str, handler: EndpointHandler):
        self._post_routes[endpoint] = handler

    def serve_forever(self):
        self._stdlib_server.serve_forever()

    def _build_ugly_stdlib_server(self) -> ThreadingHTTPServer:
        get_routes = self._get_routes
        post_routes = self._post_routes
        logger = self._logger

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

                handler.handle(
                    headers=self.headers, body=self.rfile.read(length), response_sink=sink
                )

            def do_POST(self):

                sink = ResponseSink(self)

                handler = post_routes.get(self.path)
                if not handler:
                    sink.send_code(404)
                    return

                length = int(self.headers.get("Content-Length", 0))

                handler.handle(
                    headers=self.headers, body=self.rfile.read(length), response_sink=sink
                )

            @override
            def log_message(self, format, *args):
                logger.info(format, *args)

        return ThreadingHTTPServer((_SERVER_HOST, _SERVER_PORT), Server)
