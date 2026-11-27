from typing import override
lazy import logging

import domain.task as task
import ard.api.tasks.list_tasks as list_tasks
import ard.client as agent_client


class AgentAPITaskListAdapter(task.TasksListService):
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
    def list(self) -> list[task.Task]:
        """Return the tasks configured in the agent."""
        self._logger.info("Tasks requested")

        task_list = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        tasks : list[task.Task] = []
        for t in task_list:
            tasks.append(task.Task(
                    name= t.name,
                    description=t.description,
                    recipients=t.recipients,
                    request=t.request,
                    schedule=t.schedule,
                    active = False if not isinstance(t.active,bool) else t.active,
                    oneshot = False if not isinstance(t.oneshot,bool) else t.oneshot,
                ))

        return tasks
