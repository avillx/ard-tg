from datetime import datetime
from typing import override
lazy import logging

import ard.api.activity.get_activity as get_activity
import ard.client as agent_client
import ard.models as models
from ard.types import UNSET
from domain.activity import ActivityRecord, ActivityRepo


class AgentAPIActivityRepo(ActivityRepo):
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    @override
    def get_activity(
        self,
        from_: datetime,
        to: datetime | None = None
    ) -> list[ActivityRecord]:
        """Return today's agent activity

        raise on errors abd bad validations
        """
        self._logger.info("Activity requested")
        request = models.GetActivityBody(
            from_=from_,
            to=to if to is not None else UNSET,
        )

        resp = get_activity.sync(
            client=self._agent_client,
            body=request,
        )

        # list[models.ActivityRecord] is only valid result
        # when resp is a list, then no need to handle errors
        if isinstance(resp,list):
            return cast_to_domain(resp)

        handle_errors(resp)
        return []

def cast_to_domain(resp: list[models.ActivityRecord]) -> list[ActivityRecord]:
    result: list[ActivityRecord] = []
    for record in resp:
        result.append(ActivityRecord(
            date=record.date,
            content=record.content,
        ))

    return result

def handle_errors(resp: models.Error | models.ValidationError | list[models.ActivityRecord] | None):
    match resp:
        case models.ValidationError():
            raise Exception(f"invalid request,{resp.to_dict()}")

        case models.Error():
            raise Exception(f"problem: {resp.message}")

        case _:
            raise Exception("agent api return unexpected result")
