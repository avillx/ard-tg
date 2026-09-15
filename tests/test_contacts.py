import json

from contacts import ContactService


def test_missing_file_returns_empty(tmp_path, logger):
    svc = ContactService(storage_path=str(tmp_path), logger=logger)

    assert svc.contacts() == {}


def test_add_contact_persists(tmp_path, logger):
    svc = ContactService(storage_path=str(tmp_path), logger=logger)

    svc.add_contact("123", "Alice")

    assert svc.contacts() == {"123": "Alice"}

    path = tmp_path / "telegram" / "contacts.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"123": "Alice"}


def test_add_contact_overwrites_existing(tmp_path, logger):
    svc = ContactService(storage_path=str(tmp_path), logger=logger)

    svc.add_contact("123", "Alice")
    svc.add_contact("123", "Bob")

    assert svc.contacts() == {"123": "Bob"}


def test_add_multiple_contacts(tmp_path, logger):
    svc = ContactService(storage_path=str(tmp_path), logger=logger)

    svc.add_contact("1", "A")
    svc.add_contact("2", "B")

    assert svc.contacts() == {"1": "A", "2": "B"}


def test_load_existing_contacts(tmp_path, logger):
    path = tmp_path / "telegram"
    path.mkdir(parents=True)
    (path / "contacts.json").write_text('{"1": "A", "2": "B"}', encoding="utf-8")

    svc = ContactService(storage_path=str(tmp_path), logger=logger)

    assert svc.contacts() == {"1": "A", "2": "B"}