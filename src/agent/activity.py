import datetime as dt
lazy import logging

import ard.api.activity.get_activity as get_activity
import ard.client as agent_client
import ard.models as models


class ActivityService:
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    def today_activity(self) -> list[models.ActivityRecord]:
        """Return today's agent activity

        raise on errors abd bad validations
        """
        self._logger.info("Activity requested")
        request = models.GetActivityBody(from_=dt.datetime.now(dt.UTC))

        resp = get_activity.sync(
            client=self._agent_client,
            body=request,
        )

        match resp:
            case None:
                return []

            case models.ValidationError():
                raise Exception(f"invalid request,{resp.to_dict()}")

            case models.Error():
                raise Exception(f"problem: {resp.message}")

            case _:
                pass

        return resp
