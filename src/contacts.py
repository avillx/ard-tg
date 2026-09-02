import json
import logging
import os
import pathlib


class ContactService:
    _contacts : dict[str,str]
    _file_path : str
    _logger : logging.Logger

    def __init__(
            self, file_path: str,
            logger: logging.Logger,
        ):

        self._file_path : str = os.path.join(file_path, "contacts.json")
        self._logger : logging.Logger = logger.getChild("Contacts")
        self._contacts : dict[str,str] = self._load_contacts()

    def contacts(self) -> dict[str,str]:
        return self._contacts

    def add_contact(self, chat_id: str, name: str):
        self._contacts[chat_id] = name
        self._flush_contacts()
        self._logger.warning(f"added {name}:{chat_id}")

    def _load_contacts(self) -> dict[str,str]:
        try:
            with open(self._file_path,"rb") as f:
                data = f.read()
                contacts = json.loads(data)

                if not isinstance(contacts,dict) or not contacts:
                    raise(Exception("broken contact file"))
                return contacts

        except FileNotFoundError:
            return {}

    def _flush_contacts(self):
        path = pathlib.Path(self._file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self._contacts,f,ensure_ascii=False)
