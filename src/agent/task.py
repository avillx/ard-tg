lazy import logging

import ard.api.tasks.list_tasks as list_tasks
import ard.client as agent_client
import ard.models as models


class TaskListService:
    _logger: logging.Logger
    _agent_client: agent_client.Client

    def __init__(
        self,
        client: agent_client.Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    def task_list(self) -> list[models.TaskConfig]:
        """Return the tasks configured in the agent."""
        self._logger.info("Tasks requested")

        task_list = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        return task_list
