import json
import logging

import storage

_CONTACTS_FILE = "contacts.json"


class ContactService:
    def __init__(
        self,
        storage: storage.Storage,
        logger: logging.Logger,
    ):

        self._storage = storage
        self._logger: logging.Logger = logger.getChild("Contacts")
        self._contacts: dict[str, str] = self._load_contacts()

    def contacts(self) -> dict[str, str]:
        return self._contacts

    def add_contact(self, chat_id: str, name: str):
        self._contacts[chat_id] = name
        self._flush_contacts()
        self._logger.warning(f"added {name}:{chat_id}")

    def _load_contacts(self) -> dict[str, str]:
        try:
            data = self._storage.get(_CONTACTS_FILE)
            contacts = json.loads(data)

            if not isinstance(contacts, dict) or not contacts:
                raise (Exception("broken contact file"))

            return contacts

        except FileNotFoundError:
            return {}

    def _flush_contacts(self):
        encoded_contacts = json.dumps(self._contacts, ensure_ascii=False).encode("utf-8")
        try:
            self._storage.save(_CONTACTS_FILE, encoded_contacts)
        except Exception as e:
            self._logger.error(f"can't flush contacts {e}")
