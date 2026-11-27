from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, override

from attr import dataclass

if TYPE_CHECKING:
    import logging

@dataclass
class Contact:
    chat_id: int
    name: str

class AlreadyExistContactError(ValueError):
    pass

class ContactRepo(ABC):
    @abstractmethod
    def get_contacts(self) -> list[Contact]:
        pass

    @abstractmethod
    def save_contacts(self,contacts: list[Contact]):
        pass

class ContactStore(ABC):
    @abstractmethod
    def contacts(self) -> list[Contact]:
        pass

class ContactSink(ABC):
    @abstractmethod
    def add_contact(self, chat_id: int, name: str):
        pass

class ContactService(ContactStore,ContactSink):
    _repo: ContactRepo

    def __init__(
        self,
        repo: ContactRepo,
        logger: logging.Logger,
    ):

        self._repo = repo
        self._logger: logging.Logger = logger.getChild("Contacts")

    @override
    def contacts(self) -> list[Contact]:
        return self._repo.get_contacts()

    @override
    def add_contact(self, chat_id: int, name: str):

        contacts = self._repo.get_contacts()
        exist = False
        for contact in contacts:
            if contact.chat_id == chat_id:
                exist = True
                break

        if exist:
            raise AlreadyExistContactError()

        contacts.append(Contact(
            chat_id=chat_id,
            name=name
        ))

        try:
            self._repo.save_contacts(contacts)
        except Exception as err:
            raise Exception("new contact recieved but not saved") from err

        self._logger.warning("added %s:%s", name, chat_id)
