from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.profiles import list_profiles
from ardtg.ard_api.types import Unset
from ardtg.domain.profile import Profile, ProfileRepo

if TYPE_CHECKING:
    from ardtg.ard_api import Client


class AgentAPIProfileAdapter(ProfileRepo):
    _agent_client: Client

    def __init__(self, agent_client: Client) -> None:
        self._agent_client = agent_client

    @override
    def all_profiles(self) -> list[Profile]:

        resp = list_profiles.sync(
            client=self._agent_client,
        )

        if resp is None:
            raise Exception("agent respond nothing")

        result: list[Profile] = []
        for profile_id, profile_data in resp.additional_properties.items():
            desc = "" if isinstance(profile_data.description, Unset) else profile_data.description
            result.append(
                Profile(
                    name=profile_id,
                    description=desc,
                )
            )

        return result
