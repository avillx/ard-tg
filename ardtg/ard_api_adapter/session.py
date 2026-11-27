from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.sessions import create_session
from ardtg.ard_api.models import (
    CreateSessionBody,
    CreateSessionResponse200,
    Error,
    ValidationError,
)
from ardtg.domain.session import SessionCreator

if TYPE_CHECKING:
    from ardtg.ard_api import Client


class AgentAPINewSession(SessionCreator):
    _agent_client: Client

    def __init__(self, agent_client: Client) -> None:
        super().__init__()
        self._agent_client = agent_client

    @override
    def new_session(self, profile_id: str, instruction: str) -> str:
        """Request a new session from the agent and return its id."""

        create_session_request = CreateSessionBody(
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

            case ValidationError():
                raise Exception(f"problem with session: {resp.problems}")

            case Error():
                raise Exception(f"problem with session: {resp.message}")

            case CreateSessionResponse200():
                return resp.id
