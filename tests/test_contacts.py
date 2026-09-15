import json
import logging
from pathlib import Path

from contacts import ContactService
from storage import FileStorage


def make_service(tmp_path: Path, logger: logging.Logger) -> ContactService:
    storage = FileStorage(storage_path=str(tmp_path), logger=logger)
    return ContactService(storage=storage, logger=logger)


def test_missing_file_returns_empty(tmp_path: Path, logger: logging.Logger) -> None:
    svc = make_service(tmp_path, logger)

    assert svc.contacts() == {}


def test_add_contact_persists(tmp_path: Path, logger: logging.Logger) -> None:
    svc = make_service(tmp_path, logger)

    svc.add_contact("123", "Alice")

    assert svc.contacts() == {"123": "Alice"}

    path = tmp_path / "contacts.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"123": "Alice"}


def test_add_contact_overwrites_existing(tmp_path: Path, logger: logging.Logger) -> None:
    svc = make_service(tmp_path, logger)

    svc.add_contact("123", "Alice")
    svc.add_contact("123", "Bob")

    assert svc.contacts() == {"123": "Bob"}


def test_add_multiple_contacts(tmp_path: Path, logger: logging.Logger) -> None:
    svc = make_service(tmp_path, logger)

    svc.add_contact("1", "A")
    svc.add_contact("2", "B")

    assert svc.contacts() == {"1": "A", "2": "B"}


def test_load_existing_contacts(tmp_path: Path, logger: logging.Logger) -> None:
    (tmp_path / "contacts.json").write_text('{"1": "A", "2": "B"}', encoding="utf-8")

    svc = make_service(tmp_path, logger)

    assert svc.contacts() == {"1": "A", "2": "B"}
