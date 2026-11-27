
from typing import override

import ard.models as models
from domain.session import SessionRepo
from ard.api.sessions import create_session
from ard.client import Client


class AgentAPINewSession(SessionRepo):
    _agent_client: Client

    @override
    def new_session(self,profile_id: str, instruction: str) -> str:
        """Request a new session from the agent and return its id."""

        create_session_request = models.CreateSessionBody(
            profile_id=profile_id,
            instruction=instruction,
        )

        resp = create_session.sync(
            client=self._agent_client,
            body=create_session_request,
        )

        match resp:
            case None:
                raise Exception("agent return no session")

            case models.ValidationError():
                raise Exception(f"problem with session: {resp.problems}")

            case models.Error():
                raise Exception(f"problem with session: {resp.message}")

            case models.CreateSessionResponse200():
                return resp.id
