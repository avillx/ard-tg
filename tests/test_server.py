import json
import unittest.mock

import pytest

from server import AttachSessionHandler, ContactsHandler, ResponseSink, WebhookHandler


class BytesWriter:
    def __init__(self):
        self.data = b""

    def write(self, b):
        self.data += b


class FakeHandler:
    """Duck-typed stand-in for BaseHTTPRequestHandler used by ResponseSink."""

    def __init__(self):
        self.statuses = []
        self.headers = []
        self.wfile = BytesWriter()

    def send_response(self, code):
        self.statuses.append(code)

    def send_header(self, key, value):
        self.headers.append((key, value))

    def end_headers(self):
        pass

    def send_error(self, code, explain):
        self.statuses.append(("error", code, explain))


class RecordingSink:
    """Records what the handlers write into a ResponseSink."""

    def __init__(self):
        self.calls = []

    def send_code(self, code):
        self.calls.append(("code", code))

    def send_error(self, code, explain=None):
        self.calls.append(("error", code, explain))

    def send_json(self, code, data):
        self.calls.append(("json", code, data))


def make_headers(secret_token):
    return {"X-Telegram-Bot-Api-Secret-Token": secret_token}


def attach_body(**overrides):
    body = {"session_id": "s1", "chat_id": 123, "message": "hi", "await_time": 60}
    body.update(overrides)
    return json.dumps(body).encode()


# ---------------------------------------------------------------------------
# ResponseSink
# ---------------------------------------------------------------------------


def test_response_sink_send_json():
    h = FakeHandler()
    sink = ResponseSink(h)

    sink.send_json(200, {"a": 1})

    body = json.dumps({"a": 1}).encode("utf-8")
    assert h.statuses == [200]
    assert ("Content-type", "application/json") in h.headers
    assert ("Content-Length", str(len(body))) in h.headers
    assert h.wfile.data == body


def test_response_sink_send_code():
    h = FakeHandler()
    sink = ResponseSink(h)

    sink.send_code(403)

    assert h.statuses == [403]


def test_response_sink_send_error():
    h = FakeHandler()
    sink = ResponseSink(h)

    sink.send_error(400, "boom")

    assert h.statuses == [("error", 400, "boom")]


# ---------------------------------------------------------------------------
# WebhookHandler
# ---------------------------------------------------------------------------


def test_webhook_wrong_token():
    bot = unittest.mock.Mock()
    handler = WebhookHandler(bot=bot, secret_token="secret")
    sink = RecordingSink()

    handler.handle(headers=make_headers("wrong"), body=b"{}", response_sink=sink)

    assert sink.calls == [("code", 403)]
    bot.process_new_updates.assert_not_called()


def test_webhook_valid_update():
    bot = unittest.mock.Mock()
    handler = WebhookHandler(bot=bot, secret_token="secret")
    sink = RecordingSink()

    handler.handle(headers=make_headers("secret"), body=b'{"update_id": 1}', response_sink=sink)

    assert sink.calls == [("code", 200)]
    bot.process_new_updates.assert_called_once()
    updates = bot.process_new_updates.call_args.args[0]
    assert updates[0].update_id == 1


def test_webhook_invalid_json_returns_500():
    bot = unittest.mock.Mock()
    handler = WebhookHandler(bot=bot, secret_token="secret")
    sink = RecordingSink()

    handler.handle(headers=make_headers("secret"), body=b"{not json", response_sink=sink)

    assert sink.calls == [("code", 500)]
    bot.process_new_updates.assert_not_called()


# ---------------------------------------------------------------------------
# AttachSessionHandler
# ---------------------------------------------------------------------------


def test_attach_valid():
    attach_svc = unittest.mock.Mock()
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers={}, body=attach_body(), response_sink=sink)

    attach_svc.attach.assert_called_once_with(session_id="s1", chat_id=123, message="hi", await_time=60.0)
    assert sink.calls == [("code", 200)]


def test_attach_invalid_json():
    handler = AttachSessionHandler(unittest.mock.Mock())
    sink = RecordingSink()

    handler.handle(headers={}, body=b"{bad", response_sink=sink)

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
def test_attach_validation_errors(field, value):
    handler = AttachSessionHandler(unittest.mock.Mock())
    sink = RecordingSink()

    handler.handle(headers={}, body=attach_body(**{field: value}), response_sink=sink)

    assert sink.calls[0][0] == "error"
    assert sink.calls[0][1] == 400


@pytest.mark.xfail(
    strict=True,
    reason="code bug: `not isinstance(await_time, int) or not int` — `not int` is always False; "
    "intended `not await_time` would reject await_time=0 like chat_id=0",
)
def test_attach_await_time_zero_bug():
    attach_svc = unittest.mock.Mock()
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers={}, body=attach_body(await_time=0), response_sink=sink)

    assert sink.calls == [("error", 400, "bad await time field")]


@pytest.mark.xfail(
    strict=True,
    reason="code bug: on attach error the handler sends 400 but then also 200 (missing return after except)",
)
def test_attach_service_raises_no_trailing_200():
    attach_svc = unittest.mock.Mock()
    attach_svc.attach.side_effect = Exception("boom")
    handler = AttachSessionHandler(attach_svc)
    sink = RecordingSink()

    handler.handle(headers={}, body=attach_body(), response_sink=sink)

    assert sink.calls == [("error", 400, "attach boom")]


# ---------------------------------------------------------------------------
# ContactsHandler
# ---------------------------------------------------------------------------


def test_contacts_ok():
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.return_value = {"1": "A"}
    handler = ContactsHandler(contact_svc)
    sink = RecordingSink()

    handler.handle(headers={}, body=b"", response_sink=sink)

    assert sink.calls == [("json", 200, {"contacts": {"1": "A"}})]


def test_contacts_error():
    contact_svc = unittest.mock.Mock()
    contact_svc.contacts.side_effect = Exception("boom")
    handler = ContactsHandler(contact_svc)
    sink = RecordingSink()

    handler.handle(headers={}, body=b"", response_sink=sink)

    assert sink.calls == [("code", 400)]