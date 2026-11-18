import logging
import unittest.mock

import pytest

import agent.session as session_mod
import ard.models as models
from agent.session import ProfileSource, SessionService, SystemTime, TimeProvider


class FakeTime(TimeProvider):
    """Controllable clock for SessionService tests."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def now(self) -> float:
        return self._now


class FakeProfileSource(ProfileSource):
    """Controllable profile selection for SessionService tests."""

    def __init__(self, profile_id: str = "") -> None:
        self.profile_id = profile_id

    def get_profile(self) -> str:
        return self.profile_id


def make_service(
    clock: TimeProvider,
    monkeypatch: pytest.MonkeyPatch,
    *,
    life_time: float = 10.0,
    instruction: str = "be nice",
    client: unittest.mock.Mock | None = None,
    sync_result: object = None,
    profile_source: ProfileSource | None = None,
) -> tuple[SessionService, unittest.mock.Mock, unittest.mock.Mock]:
    client = client if client is not None else unittest.mock.Mock()
    fake_sync = unittest.mock.Mock(return_value=sync_result)
    monkeypatch.setattr(session_mod.create_session, "sync", fake_sync)

    svc = SessionService(
        agent_client=client,
        profile_source=profile_source if profile_source is not None else FakeProfileSource(),
        life_time=life_time,
        instruction=instruction,
        logger=logging.getLogger("test"),
        time=clock,
    )
    return svc, fake_sync, client


def test_get_actual_creates_session_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock, monkeypatch, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    assert svc.get_actual() == "s-new"
    assert svc.get() == "s-new"
    sync.assert_called_once()


def test_create_session_passes_agent_client_and_instruction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeTime(0.0)
    client = unittest.mock.Mock()
    svc, sync, _ = make_service(
        clock,
        monkeypatch,
        client=client,
        instruction="do it",
        sync_result=models.CreateSessionResponse200(id="x"),
    )

    svc.get_actual()

    assert sync.call_args.kwargs["client"] is client
    body = sync.call_args.kwargs["body"]
    assert isinstance(body, models.CreateSessionBody)
    assert body.instruction == "do it"
    assert body.profile_id == ""
    assert body.to_dict() == {"profile_id": "", "instruction": "do it"}


def test_create_session_uses_selected_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock,
        monkeypatch,
        profile_source=FakeProfileSource("coder"),
        sync_result=models.CreateSessionResponse200(id="s-new"),
    )

    svc.get_actual()

    body = sync.call_args.kwargs["body"]
    assert body.profile_id == "coder"
    assert body.to_dict() == {"profile_id": "coder", "instruction": "be nice"}


def test_get_actual_reuses_session_within_lifetime(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch)

    svc.set("s1")
    clock._now = 3.0  # idle = 3 < 10

    assert svc.get_actual() == "s1"
    sync.assert_not_called()


def test_get_actual_boundary_exactly_lifetime_is_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch)

    svc.set("s1")
    clock._now = 10.0  # idle == life_time, strict `>` means still alive

    assert svc.get_actual() == "s1"
    sync.assert_not_called()


def test_get_actual_expires_after_lifetime(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock, monkeypatch, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    svc.set("s1")
    clock._now = 10.5  # idle > 10

    assert svc.get_actual() == "s-new"
    sync.assert_called_once()


def test_get_actual_back_to_back_uses_same_session(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock, monkeypatch, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    svc.set("s1")
    clock._now = 1.0
    assert svc.get_actual() == "s1"

    clock._now = 5.0
    assert svc.get_actual() == "s1"

    sync.assert_not_called()


def test_get_actual_keeps_session_while_profile_is_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeTime(0.0)
    profile_source = FakeProfileSource("coder")
    svc, sync, _ = make_service(
        clock,
        monkeypatch,
        profile_source=profile_source,
        sync_result=models.CreateSessionResponse200(id="s-new"),
    )

    assert svc.get_actual() == "s-new"

    clock._now = 3.0
    assert svc.get_actual() == "s-new"
    sync.assert_called_once()


def test_get_actual_recreates_session_when_profile_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeTime(0.0)
    profile_source = FakeProfileSource("coder")
    svc, sync, _ = make_service(
        clock,
        monkeypatch,
        profile_source=profile_source,
        sync_result=models.CreateSessionResponse200(id="s-new"),
    )

    svc.set("s-old")

    profile_source.profile_id = "writer"
    clock._now = 1.0

    assert svc.get_actual() == "s-new"
    sync.assert_called_once()
    assert sync.call_args.kwargs["body"].profile_id == "writer"


def test_get_actual_reuses_new_session_after_profile_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeTime(0.0)
    profile_source = FakeProfileSource("coder")
    svc, sync, _ = make_service(
        clock,
        monkeypatch,
        profile_source=profile_source,
        sync_result=models.CreateSessionResponse200(id="s-new"),
    )

    profile_source.profile_id = "writer"
    assert svc.get_actual() == "s-new"

    # the new session is bound to the new profile, so it must be reused
    clock._now = 1.0
    assert svc.get_actual() == "s-new"
    sync.assert_called_once()


def test_get_returns_without_creating(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch)

    svc.set("s1")

    assert svc.get() == "s1"
    sync.assert_not_called()


def test_drop_clears_session_and_next_get_actual_creates(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock, monkeypatch, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    svc.set("s1")
    svc.drop()

    assert svc.get() == ""

    clock._now = 1.0
    assert svc.get_actual() == "s-new"
    sync.assert_called_once()


def test_additional_time_extends_lifetime(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch, life_time=10.0)

    svc.set("s1", additional_time=5.0)
    clock._now = 12.0  # idle = 12 - 5 = 7 <= 10, valid thanks to additional_time

    assert svc.get_actual() == "s1"
    sync.assert_not_called()


def test_additional_time_boundary_idle_equals_lifetime(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch, life_time=10.0)

    svc.set("s1", additional_time=5.0)
    clock._now = 15.0  # idle = 15 - 5 = 10 == life_time, still alive

    assert svc.get_actual() == "s1"
    sync.assert_not_called()


def test_additional_time_negative_idle_still_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(clock, monkeypatch, life_time=10.0)

    svc.set("s1", additional_time=100.0)
    clock._now = 50.0  # idle = 50 - 100 = -50

    assert svc.get_actual() == "s1"
    sync.assert_not_called()


def test_get_actual_renews_window_and_consumes_additional_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeTime(0.0)
    svc, sync, _ = make_service(
        clock, monkeypatch, life_time=10.0, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    svc.set("s1", additional_time=100.0)

    clock._now = 1.0
    assert svc.get_actual() == "s1"  # additional_time is applied here
    sync.assert_not_called()

    # after access additional_time is consumed and the window restarts at t=1
    clock._now = 11.5  # idle since t=1 is 10.5 > 10
    assert svc.get_actual() == "s-new"
    sync.assert_called_once()


def test_create_session_none_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, _, _ = make_service(clock, monkeypatch, sync_result=None)

    with pytest.raises(Exception, match="agent return no session"):
        svc.get_actual()


def test_create_session_validation_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, _, _ = make_service(
        clock, monkeypatch, sync_result=models.ValidationError(problems="bad field")
    )

    with pytest.raises(Exception, match="problem with session: bad field"):
        svc.get_actual()


def test_create_session_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = FakeTime(0.0)
    svc, _, _ = make_service(
        clock, monkeypatch, sync_result=models.Error(message="agent not found")
    )

    with pytest.raises(Exception, match="problem with session: agent not found"):
        svc.get_actual()


def test_create_session_logs_id(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    clock = FakeTime(0.0)
    svc, _, _ = make_service(
        clock, monkeypatch, sync_result=models.CreateSessionResponse200(id="s-new")
    )

    with caplog.at_level(logging.INFO):
        svc.get_actual()

    assert "created new session with id: s-new" in caplog.text


def test_system_time_returns_monotonic_float() -> None:
    t = SystemTime()
    a = t.now()
    b = t.now()

    assert isinstance(a, float)
    assert b >= a
