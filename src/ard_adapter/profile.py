from typing import override

import domain.profile as profile
from ard.api.profiles import list_profiles
from ard.client import Client
from ard.types import Unset


class AgentAPIProfileAdapter(profile.ProfileRepo):
    _agent_client: Client

    def __init__(self, agent_client: Client) -> None:
        self._agent_client = agent_client

    @override
    def all_profiles(self) -> list[profile.Profile]:

        resp = list_profiles.sync(
            client=self._agent_client,
        )

        if resp is None:
            raise Exception("agent respond nothing")

        result: list[profile.Profile] = []
        for profile_id, profile_data in resp.additional_properties.items():
            desc = "" if isinstance(profile_data.description, Unset) else profile_data.description
            result.append(profile.Profile(
                name =  profile_id,
                description = desc,
            ))

        return result
