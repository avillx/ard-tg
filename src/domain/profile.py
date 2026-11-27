from abc import ABC, abstractmethod
from typing import override

from attr import dataclass

from domain.session import ProfileSource
from ard import client as agent_client


@dataclass
class Profile:
    name: str
    description: str

class ProfileRepo(ABC):
    @abstractmethod
    def all_profiles(self) -> list[Profile]:
        pass

class ProfileSetter(ABC):
    @abstractmethod
    def set_profile(self, profile_id: str):
        pass

class ProfileService(ProfileSource,ProfileRepo,ProfileSetter):
    _selected_profile: str
    _agent_client: agent_client.Client
    _profile_repo: ProfileRepo

    def __init__(self, agent_client: agent_client.Client) -> None:
        self._agent_client = agent_client
        self._selected_profile = ""

    @override
    def all_profiles(self) -> list[Profile]:
        return self._profile_repo.all_profiles()

    @override
    def set_profile(self, profile_id: str):
        # selected none profile, thats ok
        if profile_id == "":
            self._selected_profile = profile_id
            return

        found = False
        for p in self._profile_repo.all_profiles():
            if p.name == profile_id:
                found = True
                break

        if not found:
            raise ValueError("profile does not exist")

        self._selected_profile = profile_id

    @override
    def get_profile(self) -> str:
        return self._selected_profile
