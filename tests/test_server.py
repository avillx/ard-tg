from __future__ import annotations

import dataclasses
import io
import json
import logging
import signal
import unittest.mock
from collections.abc import Callable
from email.message import Message
from http.server import BaseHTTPRequestHandler
from typing import Any, cast

import pytest

import server
from server import AttachSessionHandler, BotServer, ContactsHandler, ResponseSink, WebhookHandler


class BytesWriter:
    def __init__(self) -> None:
        self.data: bytes = b""

    def write(self, b: bytes) -> None:
        self.data += b


class FakeHandler:
    """Duck-typed stand-in for BaseHTTPRequestHandler used by ResponseSink."""

    def __init__(self) -> None:
        self.statuses: list[object] = []
        self.headers: list[tuple[str, str]] = []
        self.wfile = BytesWriter()

    def send_response(self, code: int) -> None:
        self.statuses.append(code)

    def send_header(self, key: str, value: str) -> None:
        self.headers.append((key, value))

    def end_headers(self) -> None:
        pass

    def send_error(self, code: int, explain: str) -> None:
        self.statuses.append(("error", code, explain))


class RecordingSink(ResponseSink):
    """Records what the handlers write into a ResponseSink."""

    def __init__(self) -> None:
        super().__init__(cast(BaseHTTPRequestHandler, cast(object, FakeHandler())))
        self.calls: list[tuple[object, ...]] = []

    def send_code(self, code: int) -> None:
        self.calls.append(("code", code))

    def send_error(self, code: int, explain: str | None = None) -> None:
        self.calls.append(("error", code, explain))

    def send_json(self, code: int, data: Any) -> None:
        self.calls.append(("json", code, data))


def _make_sink(handler: FakeHandler) -> ResponseSink:
    return ResponseSink(cast(BaseHTTPRequestHandler, cast(object, handler)))


def make_headers(secret_token: str) -> Message[str, str]:
    headers = Message()
    headers["X-Telegram-Bot-Api-Secret-Token"] = secret_token
    return headers


def attach_body(**overrides: object) -> bytes:
    body: dict[str, object] = {
        "session_id": "s1",
        "chat_id": 123,
        "message": "hi",
        "await_time": 60,
    }
    body.update(overrides)
    return json.dumps(body).encode()


def make_webhook_handler(
    bot: Any,
    *,
    secret_token: str = "secret",
    url: str = "https://example.com",
    webhook_path: str = "/bot/hook",
) -> WebhookHandler:
    """Builds a WebhookHandler with a deterministic secret token."""

    with unittest.mock.patch("server.secrets.token_hex", return_value=secret_token):
        return WebhookHandler(bot=bot, url=url, webhook_path=webhook_path)


@dataclasses.dataclass
class Exchange:
    """Result of driving one request through the real route dispatch."""

    status: int | None = None
    headers: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    body: bytes = b""
    error: tuple[int | None, str | None] | None = None


class HTTPTestClient:
    """Drives a BaseHTTPRequestHandler subclass without opening a socket."""

    def __init__(self, handler_cls: type[BaseHTTPRequestHandler]) -> None:
        self._handler_cls = handler_cls

    def get(self, path: str, headers: dict[str, str] | None = None) -> Exchange:
        return self._dispatch("GET", path, headers=headers)

    def post(self, path: str, body: bytes = b"", headers: dict[str, str] | None = None) -> Exchange:
        return self._dispatch("POST", path, body=body, headers=headers)

    def _dispatch(
        self,
        method: str,
        path: str,
        *,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> Exchange:
        exchange = Exchange()
        handler: Any = self._handler_cls.__new__(self._handler_cls)
        handler.path = path
        handler.headers = Message()
        handler.headers["Content-Length"] = str(len(body))
        for key, value in (headers or {}).items():
            handler.headers[key] = value
        handler.rfile = io.BytesIO(body)
        handler.wfile = BytesWriter()
        handler.log_message = lambda *args: None
        handler.send_response = lambda code, message=None: setattr(exchange, "status", code)
        handler.send_header = lambda key, value: exchange.headers.append((key, value))
        handler.end_headers = lambda: None
        handler.send_error = lambda code=None, message=None, explain=None: setattr(
            exchange, "error", (code, explain)
        )

        getattr(handler, f"do_{method}")()
        exchange.body = handler.wfile.data
        return exchange


class FakeHTTPServer:
    """Stand-in for ThreadingHTTPServer that captures the built routes."""

    instances: list[FakeHTTPServer] = []

    def __init__(self, address: tuple[str, int], handler_cls: type[BaseHTTPRequestHandler]) -> None:
        self.address = address
        self.handler_cls = handler_cls
        self.serve_count = 0
        self.failure: Exception | None = None
        self.on_serve: Callable[[], None] | None = None
        FakeHTTPServer.instances.append(self)

    @classmethod
    def latest(cls) -> FakeHTTPServer:
        assert cls.instances, "build_server() was not called"
        return cls.instances[-1]

    def client(self) -> HTTPTestClient:
        return HTTPTestClient(self.handler_cls)

    def serve_forever(self) -> None:
        self.serve_count += 1
        if self.on_serve is not None:
            self.on_serve()
        if self.failure is not None:
            raise self.failure


class FakeThread:
    """Stand-in for threading.Thread that runs its target synchronously on start."""

    instances: list[FakeThread] = []

    def __init__(self, target: Callable[[], None], daemon: bool | None = None, **kwargs: Any):
        self.target = target
        self.daemon = daemon
        self.started = False
        FakeThread.instances.append(self)

    def start(self) -> None:
        self.started = True
        self.target()


@pytest.fixture
def fake_http(monkeypatch: pytest.MonkeyPatch) -> type[FakeHTTPServer]:
    """Replaces the real HTTP server so BotServer never binds a port."""

    monkeypatch.setattr(server, "ThreadingHTTPServer", FakeHTTPServer)
    FakeHTTPServer.instances.clear()
    FakeThread.instances.clear()
    return FakeHTTPServer


def _or_mock(value: Any) -> Any:
    return unittest.mock.Mock() if value is None else value


def make_bot_server(
    *,
    webhook_url: str = "",
    bot: Any = None,
    notifier: Any = None,
    attachment_service: Any = None,
    contact_service: Any = None,
    logger: logging.Logger | None = None,
) -> BotServer:
    return BotServer(
        attachment_service=_or_mock(attachment_service),
        contact_service=_or_mock(contact_service),
        notifier=_or_mock(notifier),
        webhook_url=webhook_url,
        bot=_or_mock(bot),
        logger=logger or logging.getLogger("test"),
    )


def test_response_sink_send_json() -> None:
    h = FakeHandler()
    sink = _make_sink(h)

    sink.send_json(200, {"a": 1})

    body = json.dumps({"a": 1}).encode("utf-8")
    assert h.statuses == [200]
    assert ("Content-type", "application/json") in h.headers
    assert ("Content-Length", str(len(body))) in h.headers
    assert h.wfile.data == body


def test_response_sink_send_code() -> None:
    h = FakeHandler()
    sink = _make_sink(h)

    sink.send_code(403)

    assert h.statuses == [403]


def test_response_sink_send_error() -> None:
    h = FakeHandler()
    sink = _make_sink(h)

    sink.send_error(400, "boom")

    assert h.statuses == [("error", 400, "boom")]


def test_webhook_registers_itself_on_start() -> None:
    bot = unittest.mock.Mock()

    _ = make_webhook_handler(bot)

    bot.remove_webhook.assert_called_once_with()
    bot.set_webhook.assert_called_once_with(
        url="https://example.com/bot/hook",
        secret_token="secret",
    )


def test_webhook_wrong_token() -> None:
    bot = unittest.mock.Mock()
    handler = make_webhook_handler(bot)
    sink = RecordingSink()

    handler.handle(headers=make_headers("wrong"), body=b"{}", response_sink=sink)

    assert sink.calls == [("code", 403)]
    bot.process_new_updates.assert_not_called()


def test_webhook_valid_update() -> None:
    bot = unittest.mock.Mock()
    handler = make_webhook_handler(bot)
    sink = RecordingSink()

    handler.handle(headers=make_headers("secret"), body=b'{"update_id": 1}', response_sink=sink)

    assert sink.calls == [("code", 200)]
    bot.process_new_updates.assert_called_once()
    updates = bot.process_new_updates.call_args.args[0]
    assert updates[0].update_id == 1


def test_webhook_invalid_json_returns_500() -> None:
    bot = unittest.mock.Mock()
    handler = make_webhook_handler(bot)
    sink = RecordingSink()

    handler.handle(headers=make_headers("secret"), body=b"{not json", response_sink=sink)

    assert sink.calls == [("code", 500)]
    bot.process_new_updates.assert_not_called()


def test_attach_valid() -> None:
    attach_svc = unittest.mock.Mock()
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers=Message(), body=attach_body(), response_sink=sink)

    attach_svc.attach.assert_called_once_with(
        session_id="s1", chat_id=123, message="hi", await_time=60.0
    )
    assert sink.calls == [("code", 200)]


def test_attach_invalid_json() -> None:
    handler = AttachSessionHandler(unittest.mock.Mock())
    sink = RecordingSink()

    handler.handle(headers=Message(), body=b"{bad", response_sink=sink)

    assert sink.calls == [("code", 400)]


@pytest.mark.parametrize(
    "field,value",
    [
        ("session_id", ""),
        ("session_id", 123),
        ("chat_id", "abc"),
        ("chat_id", 0),
        ("message", ""),
        ("message", None),
    ],
)
def test_attach_validation_errors(field: str, value: object) -> None:
    handler = AttachSessionHandler(unittest.mock.Mock())
    sink = RecordingSink()

    handler.handle(headers=Message(), body=attach_body(**{field: value}), response_sink=sink)

    assert sink.calls[0][0] == "error"
    assert sink.calls[0][1] == 400


@pytest.mark.xfail(
    strict=True,
    reason="code bug: `not isinstance(await_time, int) or not int` — `not int` is always False; "
    "intended `not await_time` would reject await_time=0 like chat_id=0",
)
def test_attach_await_time_zero_bug() -> None:
    attach_svc = unittest.mock.Mock()
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers=Message(), body=attach_body(await_time=0), response_sink=sink)

    assert sink.calls == [("error", 400, "bad await time field")]


def test_attach_service_raises_no_trailing_200() -> None:
    attach_svc = unittest.mock.Mock()
    attach_svc.attach.side_effect = Exception("boom")
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers=Message(), body=attach_body(), response_sink=sink)

    assert sink.calls == [("error", 400, "attach boom")]


def test_contacts_ok() -> None:
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {"1": "A"}
    handler = ContactsHandler(contact_svc)
    sink = RecordingSink()

    handler.handle(headers=Message(), body=b"", response_sink=sink)

    assert sink.calls == [("json", 200, {"contacts": {"1": "A"}})]


def test_contacts_error() -> None:
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.side_effect = Exception("boom")
    handler = ContactsHandler(contact_svc)
    sink = RecordingSink()

    handler.handle(headers=Message(), body=b"", response_sink=sink)

    assert sink.calls == [("code", 400)]


def test_http_server_routes(fake_http: type[FakeHTTPServer]) -> None:
    attach_svc = unittest.mock.Mock()
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {"1": "Alice"}

    _ = make_bot_server(attachment_service=attach_svc, contact_service=contact_svc)

    http_server = fake_http.latest()
    assert http_server.address == ("0.0.0.0", 8443)
    client = http_server.client()

    assert client.get("/health").status == 200

    contacts = client.get("/contacts")
    assert contacts.status == 200
    assert ("Content-type", "application/json") in contacts.headers
    assert json.loads(contacts.body) == {"contacts": {"1": "Alice"}}

    attach = client.post("/attach", body=attach_body())
    assert attach.status == 200
    attach_svc.attach.assert_called_once_with(
        session_id="s1", chat_id=123, message="hi", await_time=60.0
    )

    bad_attach = client.post("/attach", body=attach_body(chat_id="nope"))
    assert bad_attach.status is None
    assert bad_attach.error == (400, "bad chat_id field")
    attach_svc.attach.assert_called_once()

    assert client.get("/unknown").status == 404
    assert client.post("/unknown", body=b"{}").status == 404


def test_polling_mode_has_no_webhook_route(fake_http: type[FakeHTTPServer]) -> None:
    bot = unittest.mock.Mock()

    _ = make_bot_server(bot=bot)

    bot.set_webhook.assert_not_called()
    assert fake_http.latest().client().post("/bot/any", body=b"{}").status == 404


def test_webhook_mode_serves_telegram_updates(fake_http: type[FakeHTTPServer]) -> None:
    bot = unittest.mock.Mock()

    _ = make_bot_server(webhook_url="https://bot.example.com", bot=bot)

    bot.remove_webhook.assert_called_once_with()
    bot.set_webhook.assert_called_once()
    url: str = bot.set_webhook.call_args.kwargs["url"]
    secret: str = bot.set_webhook.call_args.kwargs["secret_token"]
    webhook_path = url.removeprefix("https://bot.example.com")
    assert webhook_path.startswith("/bot/")

    client = fake_http.latest().client()

    accepted = client.post(
        webhook_path,
        body=b'{"update_id": 7}',
        headers={"X-Telegram-Bot-Api-Secret-Token": secret},
    )
    assert accepted.status == 200
    updates = bot.process_new_updates.call_args.args[0]
    assert updates[0].update_id == 7

    denied = client.post(
        webhook_path,
        body=b"{}",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert denied.status == 403


def test_run_polling_mode(fake_http: type[FakeHTTPServer]) -> None:
    bot = unittest.mock.Mock()
    notifier = unittest.mock.Mock()
    srv = make_bot_server(bot=bot, notifier=notifier)
    http_server = fake_http.latest()

    with (
        unittest.mock.patch("server.signal.signal") as signal_mock,
        unittest.mock.patch("server.threading.Thread", FakeThread),
    ):
        srv.run()

    assert signal_mock.call_args.args[0] == signal.SIGTERM

    thread = FakeThread.instances[0]
    assert thread.daemon is True
    assert thread.started
    assert http_server.serve_count == 1

    bot.infinity_polling.assert_called_once_with(none_stop=True)
    notifier.notify_about_up.assert_called_once_with()
    notifier.notify_about_down.assert_called_once_with()


def test_run_webhook_mode(fake_http: type[FakeHTTPServer]) -> None:
    bot = unittest.mock.Mock()
    notifier = unittest.mock.Mock()
    srv = make_bot_server(webhook_url="https://bot.example.com", bot=bot, notifier=notifier)
    http_server = fake_http.latest()

    with (
        unittest.mock.patch("server.signal.signal"),
        unittest.mock.patch("server.threading.Thread", FakeThread),
    ):
        srv.run()

    assert http_server.serve_count == 1
    assert FakeThread.instances == []
    bot.infinity_polling.assert_not_called()
    notifier.notify_about_up.assert_called_once_with()
    notifier.notify_about_down.assert_called_once_with()


def test_run_notifies_down_once_on_sigterm(fake_http: type[FakeHTTPServer]) -> None:
    notifier = unittest.mock.Mock()
    srv = make_bot_server(webhook_url="https://bot.example.com", notifier=notifier)
    http_server = fake_http.latest()
    handlers: list[Callable[[int, Any], None]] = []

    def remember_handler(_signum: int, handler: Callable[[int, Any], None]):
        handlers.append(handler)

    def dispatch_sigterm() -> None:
        handlers[0](signal.SIGTERM, None)

    http_server.on_serve = dispatch_sigterm

    with (
        unittest.mock.patch("server.signal.signal", side_effect=remember_handler),
        pytest.raises(SystemExit),
    ):
        srv.run()

    notifier.notify_about_down.assert_called_once_with()


def test_run_notifies_down_when_polling_fails(fake_http: type[FakeHTTPServer]) -> None:
    notifier = unittest.mock.Mock()
    bot = unittest.mock.Mock()
    bot.infinity_polling.side_effect = RuntimeError("boom")
    srv = make_bot_server(bot=bot, notifier=notifier)

    with (
        unittest.mock.patch("server.signal.signal"),
        unittest.mock.patch("server.threading.Thread", FakeThread),
        pytest.raises(RuntimeError, match="boom"),
    ):
        srv.run()

    notifier.notify_about_up.assert_called_once_with()
    notifier.notify_about_down.assert_called_once_with()


def test_serve_http_logs_and_reraises(
    fake_http: type[FakeHTTPServer], caplog: pytest.LogCaptureFixture
) -> None:
    srv = make_bot_server()
    fake_http.latest().failure = RuntimeError("socket is gone")

    with (
        caplog.at_level(logging.ERROR, logger="test"),
        pytest.raises(RuntimeError, match="socket is gone"),
    ):
        srv.serve_http()

    assert "socket is gone" in caplog.text
    assert any(record.levelno == logging.ERROR for record in caplog.records)
