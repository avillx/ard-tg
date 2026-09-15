import unittest.mock

import pytest

import agent.event as event
import arch_agent.models as models
from helpers import FakeTool, FailingTool

CLIENT = object()


class RecordingHandler(event.EventHandler):
    def __init__(self):
        self.calls = []

    def process_loop_exit(self, e):
        self.calls.append(("loop_exit", e))

    def process_compaction(self, e):
        self.calls.append(("compaction", e))

    def process_completion(self, e):
        self.calls.append(("completion", e))

    def process_completion_mistake(self, e):
        self.calls.append(("completion_mistake", e))

    def process_tool_error(self, e):
        self.calls.append(("tool_error", e))

    def process_tool_result(self, e):
        self.calls.append(("tool_result", e))

    def process_error(self, e):
        self.calls.append(("error", e))


# ---------------------------------------------------------------------------
# determine_response
# ---------------------------------------------------------------------------


def test_done_returns_none():
    assert event.determine_response("data: [DONE]") is None


def test_non_data_line_returns_none():
    assert event.determine_response("") is None
    assert event.determine_response(": keep-alive") is None
    assert event.determine_response("random text") is None


def test_completion_event_parsed():
    ev = event.determine_response(
        'data: {"type": "complete", "done": false, "completion": "hi", "tool_calls": []}'
    )
    assert isinstance(ev, models.CompletionEvent)
    assert ev.completion == "hi"


def test_loop_exit_event_parsed():
    ev = event.determine_response('data: {"type": "loop_exit"}')
    assert isinstance(ev, models.LoopExitEvent)


def test_loop_exit_event_with_cause():
    ev = event.determine_response('data: {"type": "loop_exit", "cause": "boom"}')
    assert isinstance(ev, models.LoopExitEvent)
    assert ev.cause == "boom"


def test_compaction_event_parsed():
    ev = event.determine_response('data: {"type": "compaction", "message": "m", "result": "r"}')
    assert isinstance(ev, models.CompactionEvent)
    assert ev.result == "r"


def test_tool_error_event_parsed():
    ev = event.determine_response('data: {"type": "tool_error", "cause": "c", "tool_name": "t", "args": ""} ')
    assert isinstance(ev, models.ToolErrorEvent)
    assert ev.cause == "c"


def test_provided_toolcall_event_parsed():
    ev = event.determine_response(
        'data: {"type": "provided_toolcall", "tool": "t", "agent_id": "a", "session_id": "s"}'
    )
    assert isinstance(ev, models.ProvidedToolCallEvent)


def test_tool_result_event_parsed():
    ev = event.determine_response('data: {"type": "tool_result", "id": "i", "result": []}')
    assert isinstance(ev, models.ToolResultEvent)


def test_completion_mistake_event_parsed():
    ev = event.determine_response('data: {"type": "complete_mistake", "error": "e"}')
    assert isinstance(ev, models.CompletionMistakeEvent)


def test_error_event_parsed():
    ev = event.determine_response('error: {"message": "boom"}')
    assert isinstance(ev, models.Error)
    assert ev.message == "boom"


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        event.determine_response('data: {"type": "nope"}')


def test_malformed_data_json_raises():
    with pytest.raises(ValueError):
        event.determine_response("data: {not json")


# ---------------------------------------------------------------------------
# AgentEventHandler
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ev,method",
    [
        (models.CompletionEvent(type_=models.CompletionEventType.COMPLETE, done=False, completion="x", tool_calls=[]), "completion"),
        (models.CompletionMistakeEvent(type_=models.CompletionMistakeEventType.COMPLETE_MISTAKE, error="e"), "completion_mistake"),
        (models.CompactionEvent(type_=models.CompactionEventType.COMPACTION, message="m", result="r"), "compaction"),
        (models.LoopExitEvent(type_=models.LoopExitEventType.LOOP_EXIT), "loop_exit"),
        (models.ToolResultEvent(type_=models.ToolResultEventType.TOOL_RESULT, id="i", result=[]), "tool_result"),
        (models.ToolErrorEvent(type_=models.ToolErrorEventType.TOOL_ERROR, cause="c", tool_name="t", args=""), "tool_error"),
        (models.Error(message="boom"), "error"),
    ],
)
def test_process_event_dispatches(ev, method):
    handler = RecordingHandler()
    aeh = event.AgentEventHandler(client=CLIENT, event_handler=handler, provided_tools=[])

    aeh.process_event(ev)

    assert handler.calls == [(method, ev)]


def test_process_event_unknown_raises():
    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[])

    class Weird:
        pass

    with pytest.raises(Exception):
        aeh.process_event(Weird())


def test_allowed_tool_servers():
    t1 = FakeTool(name="t1", description="desc1", schema={"type": "object", "properties": {}})
    t2 = FakeTool(name="t2", description="desc2", schema={"type": "string"})
    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[t1, t2])

    servers = aeh.allowed_tool_servers()

    assert len(servers) == 1
    tools = servers[0].tools
    assert [t.name for t in tools] == ["t1", "t2"]
    assert tools[0].description == "desc1"
    assert tools[0].schema.to_dict() == {"type": "object", "properties": {}}


def test_allowed_tool_servers_empty():
    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[])

    servers = aeh.allowed_tool_servers()

    assert len(servers) == 1
    assert servers[0].tools == []


def test_provided_toolcall_known(monkeypatch):
    sync_mock = unittest.mock.Mock()
    monkeypatch.setattr(event.tool_result, "sync", sync_mock)

    t = FakeTool(name="send_sticker", result="sticker sended")
    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[t])
    ev = models.ProvidedToolCallEvent(
        type_=models.ProvidedToolCallEventType.PROVIDED_TOOLCALL,
        tool="send_sticker",
        agent_id="a",
        session_id="s",
        args=models.ProvidedToolCallEventArgs.from_dict({"emoji": "😀"}),
        result_id="r1",
    )

    aeh.process_event(ev)

    assert t.executed_args == {"emoji": "😀"}
    sync_mock.assert_called_once()
    kwargs = sync_mock.call_args.kwargs
    assert kwargs["id"] == "r1"
    assert kwargs["client"] is CLIENT
    assert isinstance(kwargs["body"], models.ToolResultPayload)
    assert kwargs["body"].result[0].text == "sticker sended"


def test_provided_toolcall_exec_error(monkeypatch):
    sync_mock = unittest.mock.Mock()
    monkeypatch.setattr(event.tool_result, "sync", sync_mock)

    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[FailingTool(name="boom")])
    ev = models.ProvidedToolCallEvent(
        type_=models.ProvidedToolCallEventType.PROVIDED_TOOLCALL,
        tool="boom",
        agent_id="a",
        session_id="s",
        args=models.ProvidedToolCallEventArgs.from_dict({}),
        result_id="r2",
    )

    aeh.process_event(ev)

    assert sync_mock.call_args.kwargs["body"].result[0].text == "error: kaboom"


@pytest.mark.xfail(
    strict=True,
    reason="code bug: builds message with local 'tool' (None) instead of event.tool",
)
def test_provided_toolcall_unknown(monkeypatch):
    sync_mock = unittest.mock.Mock()
    monkeypatch.setattr(event.tool_result, "sync", sync_mock)

    aeh = event.AgentEventHandler(client=CLIENT, event_handler=RecordingHandler(), provided_tools=[])
    ev = models.ProvidedToolCallEvent(
        type_=models.ProvidedToolCallEventType.PROVIDED_TOOLCALL,
        tool="unknown",
        agent_id="a",
        session_id="s",
        result_id="r3",
    )

    aeh.process_event(ev)

    assert sync_mock.call_args.kwargs["body"].result[0].text == "tool 'unknown' is not exist"


# ---------------------------------------------------------------------------
# ConsolidationEventHandler
# ---------------------------------------------------------------------------


class _RecordingConsolidation(event.ConsolidationEventHandler):
    def __init__(self):
        super().__init__()
        self.completions = []
        self.errors = []

    def _process_completion(self, e):
        self.completions.append(e)

    def _process_error(self, e):
        self.errors.append(e)


def test_consolidation_handler_dispatch():
    h = _RecordingConsolidation()

    h.process_event(models.CompletionEvent(type_=models.CompletionEventType.COMPLETE, done=False, completion="x", tool_calls=[]))
    h.process_event(models.Error(message="boom"))

    assert len(h.completions) == 1
    assert len(h.errors) == 1


def test_consolidation_handler_unknown_raises():
    class H(event.ConsolidationEventHandler):
        def _process_completion(self, e):
            pass

        def _process_error(self, e):
            pass

    h = H()

    with pytest.raises(Exception):
        h.process_event(models.LoopExitEvent(type_=models.LoopExitEventType.LOOP_EXIT))