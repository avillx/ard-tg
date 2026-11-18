from typing import override

import ard.types as ard_types
from agent.session import ProfileSource
from ard import client as agent_client
from ard.api.profiles import list_profiles


class ProfileService(ProfileSource):
    _selected_profile: str
    _agent_client: agent_client.Client

    def __init__(self, agent_client: agent_client.Client) -> None:
        self._agent_client = agent_client
        self._selected_profile = ""

    def all_profiles(self) -> dict[str, str]:

        resp = list_profiles.sync(
            client=self._agent_client,
        )

        if resp is None:
            raise Exception("agent respond nothing")

        profiles: dict[str, str] = {}

        for profile_id, profile in resp.additional_properties.items():
            desc = "" if isinstance(profile.description, ard_types.Unset) else profile.description
            profiles[profile_id] = desc

        return profiles

    def set_profile(self, profile_id: str):
        # selected none profile, thats ok
        if profile_id == "":
            self._selected_profile = profile_id
            return

        if self.all_profiles().get(profile_id) is None:
            raise ValueError("profile does not exist")
        self._selected_profile = profile_id

    @override
    def get_profile(self) -> str:
        return self._selected_profile
