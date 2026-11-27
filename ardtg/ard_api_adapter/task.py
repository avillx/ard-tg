from typing import TYPE_CHECKING, override

from ardtg.ard_api.api.tasks import list_tasks
from ardtg.domain.task import Task, TasksListService

if TYPE_CHECKING:
    import logging

    from ardtg.ard_api import Client

class AgentAPITaskListAdapter(TasksListService):
    _logger: logging.Logger
    _agent_client: Client

    def __init__(
        self,
        client: Client,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger
        self._agent_client = client

    @override
    def list(self) -> list[Task]:
        """Return the tasks configured in the agent."""
        self._logger.info("Tasks requested")

        task_list = list_tasks.sync(client=self._agent_client)
        if task_list is None:
            return []

        tasks : list[Task] = []
        for t in task_list:
            tasks.append(Task(
                    name= t.name,
                    description=t.description,
                    recipients=t.recipients,
                    request=t.request,
                    schedule=t.schedule,
                    active = False if not isinstance(t.active,bool) else t.active,
                    oneshot = False if not isinstance(t.oneshot,bool) else t.oneshot,
                ))

        return tasks
