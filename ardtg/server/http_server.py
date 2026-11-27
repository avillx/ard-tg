import json
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    import logging
    from email.message import Message

# The bot must accept webhook and attach calls from outside, so listen on every interface.
_SERVER_HOST = "0.0.0.0"  # noqa: S104
_SERVER_PORT = 8443


class Response:
    _code: int
    def __init__(self,code: int) -> None:
        self._code = code

    def send(self,hanlder: BaseHTTPRequestHandler):
        hanlder.send_response(self._code)
        hanlder.end_headers()


class ErrorResponse(Response):
    _problem: str
    def __init__(self, code: int, problem: str) -> None:
        super().__init__(code)
        self._problem = problem

    @override
    def send(self,hanlder: BaseHTTPRequestHandler):
        hanlder.send_error(code=self._code, explain=self._problem)
        hanlder.end_headers()


class JSONResponse(Response):
    _content: dict[str,Any] # pyright: ignore[reportExplicitAny]
    def __init__(self, code: int, content: dict[str,Any]) -> None: # pyright: ignore[reportExplicitAny]
        super().__init__(code)
        self._content = content

    @override
    def send(self,hanlder: BaseHTTPRequestHandler):
        response_body = json.dumps(self._content).encode("utf-8")

        hanlder.send_response(self._code)
        hanlder.send_header("Content-type", "application/json")
        hanlder.send_header("Content-Length", str(len(response_body)))
        hanlder.end_headers()

        _ = hanlder.wfile.write(response_body)


class EndpointHandler(ABC):
    @abstractmethod
    def handle(self, headers: "Message[str, str]", body: bytes) -> Response:  # noqa
        pass


class NiceHTTPServer:
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

        class HTTPRequestHandler(BaseHTTPRequestHandler):
            def __init__(self, request, client_address, server):  # pyright: ignore[reportMissingParameterType, reportAny]
                super().__init__(request, client_address, server)

            def do_GET(self):

                handler = get_routes.get(self.path)
                if handler is None:
                    self.send_response(404)
                    self.end_headers()
                    return

                length = int(self.headers.get("Content-Length", 0))
                response = handler.handle(self.headers, self.rfile.read(length))
                response.send(self)

            def do_POST(self):

                handler = post_routes.get(self.path)
                if handler is None:
                    self.send_response(404)
                    self.end_headers()
                    return

                length = int(self.headers.get("Content-Length", 0))
                response = handler.handle(self.headers, self.rfile.read(length))
                response.send(self)

            @override
            def log_message(self, format: str, *args):  # pyright: ignore[reportAny, reportMissingParameterType]
                logger.info(format, *args)  # pyright: ignore[reportAny]

        return ThreadingHTTPServer((_SERVER_HOST, _SERVER_PORT), HTTPRequestHandler)
