from abc import ABC, abstractmethod
from typing import override

from attr import dataclass


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    description: str


class ProfileStatement(ABC):
    @abstractmethod
    def get_selected_profile(self) -> str:
        pass


class ProfileRepo(ABC):
    @abstractmethod
    def all_profiles(self) -> list[Profile]:
        pass


class ProfileSetter(ABC):
    @abstractmethod
    def set_profile(self, profile_id: str):
        pass


class ProfileService(ProfileStatement, ProfileSetter):
    _selected_profile: str
    _profile_repo: ProfileRepo

    def __init__(self, profile_repo: ProfileRepo) -> None:
        self._profile_repo = profile_repo
        self._selected_profile = ""

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
    def get_selected_profile(self) -> str:
        return self._selected_profile
