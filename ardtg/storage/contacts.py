import json
from typing import TYPE_CHECKING, Any, cast, override

from ardtg.domain.contacts import Contact, ContactRepo

if TYPE_CHECKING:
    from ardtg.storage.filestorage import Storage

_CONTACTS_FILE = "contacts.json"


class ContactJSONStorage(ContactRepo):
    _storage: Storage

    def __init__(self, _storage: Storage) -> None:
        super().__init__()
        self._storage = _storage

    @override
    def get_contacts(self) -> list[Contact]:
        try:
            data = self._storage.get(_CONTACTS_FILE)
            contacts_raw = json.loads(data)  # pyright: ignore[reportAny]
            contacts_list: list[Contact] = _parse_contacts(contacts_raw)
        except ValueError as err:
            raise ValueError("broken contact file syntax") from err
        except FileNotFoundError:
            return []

        return contacts_list

    @override
    def save_contacts(self, contacts: list[Contact]):
        encoded_contacts = json.dumps(contacts, ensure_ascii=False).encode("utf-8")
        self._storage.save(_CONTACTS_FILE, encoded_contacts)


def _parse_contact(raw: object) -> Contact:
    if not isinstance(raw, dict):
        raise ValueError(f"contact must be object, got {type(raw).__name__}")

    item: dict[str, object] = cast("dict[str, object]", raw)
    chat_id = item.get("chat_id")
    name = item.get("name")

    if not isinstance(chat_id, int) or isinstance(chat_id, bool):
        raise ValueError(f"contact.chat_id must be int, got {chat_id!r}")
    if not isinstance(name, str):
        raise ValueError(f"contact.name must be str, got {name!r}")

    return Contact(chat_id=chat_id, name=name)


def _parse_contacts(raw: Any) -> list[Contact]:  # pyright: ignore[reportExplicitAny,reportAny]
    if not isinstance(raw, list):
        raise ValueError(f"contacts must be array, got {type(raw).__name__}")  # pyright: ignore[reportAny]

    return [_parse_contact(item) for item in cast("list[object]", raw)]
