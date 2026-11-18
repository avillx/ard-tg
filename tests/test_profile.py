import unittest.mock

import pytest

import agent.profile as profile_mod
import ard.models as models
from agent.profile import ProfileService


def make_service(
    monkeypatch: pytest.MonkeyPatch,
    *,
    client: unittest.mock.Mock | None = None,
    sync_result: object = None,
) -> tuple[ProfileService, unittest.mock.Mock]:
    client = client if client is not None else unittest.mock.Mock()
    fake_sync = unittest.mock.Mock(return_value=sync_result)
    monkeypatch.setattr(profile_mod.list_profiles, "sync", fake_sync)

    return ProfileService(agent_client=client), fake_sync


def test_no_profile_selected_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    svc, sync = make_service(monkeypatch)

    assert svc.get_profile() == ""
    sync.assert_not_called()


def test_all_profiles_maps_ids_to_descriptions(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = models.ListProfilesResponse200.from_dict(
        {
            "coder": {"model": "gpt-4", "description": "writes code"},
            "writer": {"model": "gpt-4o"},
        }
    )
    client = unittest.mock.Mock()
    svc, sync = make_service(monkeypatch, client=client, sync_result=resp)

    assert svc.all_profiles() == {"coder": "writes code", "writer": ""}
    sync.assert_called_once_with(client=client)


def test_all_profiles_raises_when_agent_returns_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    svc, _ = make_service(monkeypatch, sync_result=None)

    with pytest.raises(Exception, match="agent respond nothing"):
        _ = svc.all_profiles()


def test_set_profile_selects_existing_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = models.ListProfilesResponse200.from_dict({"coder": {"model": "gpt-4"}})
    svc, _ = make_service(monkeypatch, sync_result=resp)

    svc.set_profile("coder")

    assert svc.get_profile() == "coder"


def test_set_profile_unknown_raises_and_keeps_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resp = models.ListProfilesResponse200.from_dict({"coder": {"model": "gpt-4"}})
    svc, _ = make_service(monkeypatch, sync_result=resp)
    svc.set_profile("coder")

    with pytest.raises(ValueError, match="profile does not exist"):
        svc.set_profile("nope")

    assert svc.get_profile() == "coder"


def test_set_profile_empty_clears_selection_without_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resp = models.ListProfilesResponse200.from_dict({"coder": {"model": "gpt-4"}})
    svc, sync = make_service(monkeypatch, sync_result=resp)
    svc.set_profile("coder")
    sync.reset_mock()

    svc.set_profile("")

    assert svc.get_profile() == ""
    sync.assert_not_called()
