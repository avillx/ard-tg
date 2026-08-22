from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.task_config import TaskConfig
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    name: str,
    *,
    body: TaskConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/task/{name}".format(
            name=quote(str(name), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ValidationError | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = ValidationError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: TaskConfig,
) -> Response[Any | ValidationError]:
    """Create a task

     Creates a periodic autonomous task for the agent. Tasks are executed on a cron schedule
    and can send requests to one or more agent recipients. The task name in the path
    and the `name` field in the body must match.

    Args:
        name (str):
        body (TaskConfig): Configuration for a periodic autonomous task.
            Tasks are executed on a cron schedule and send requests to agent recipients.
             Example: {'name': 'daily_report', 'description': 'Generate daily activity report',
            'recipients': ['agent_main'], 'schedule': '0 9 * * 1', 'request': 'Generate the daily
            report', 'active': True, 'oneshot': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: TaskConfig,
) -> Any | ValidationError | None:
    """Create a task

     Creates a periodic autonomous task for the agent. Tasks are executed on a cron schedule
    and can send requests to one or more agent recipients. The task name in the path
    and the `name` field in the body must match.

    Args:
        name (str):
        body (TaskConfig): Configuration for a periodic autonomous task.
            Tasks are executed on a cron schedule and send requests to agent recipients.
             Example: {'name': 'daily_report', 'description': 'Generate daily activity report',
            'recipients': ['agent_main'], 'schedule': '0 9 * * 1', 'request': 'Generate the daily
            report', 'active': True, 'oneshot': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ValidationError
    """

    return sync_detailed(
        name=name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: TaskConfig,
) -> Response[Any | ValidationError]:
    """Create a task

     Creates a periodic autonomous task for the agent. Tasks are executed on a cron schedule
    and can send requests to one or more agent recipients. The task name in the path
    and the `name` field in the body must match.

    Args:
        name (str):
        body (TaskConfig): Configuration for a periodic autonomous task.
            Tasks are executed on a cron schedule and send requests to agent recipients.
             Example: {'name': 'daily_report', 'description': 'Generate daily activity report',
            'recipients': ['agent_main'], 'schedule': '0 9 * * 1', 'request': 'Generate the daily
            report', 'active': True, 'oneshot': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: TaskConfig,
) -> Any | ValidationError | None:
    """Create a task

     Creates a periodic autonomous task for the agent. Tasks are executed on a cron schedule
    and can send requests to one or more agent recipients. The task name in the path
    and the `name` field in the body must match.

    Args:
        name (str):
        body (TaskConfig): Configuration for a periodic autonomous task.
            Tasks are executed on a cron schedule and send requests to agent recipients.
             Example: {'name': 'daily_report', 'description': 'Generate daily activity report',
            'recipients': ['agent_main'], 'schedule': '0 9 * * 1', 'request': 'Generate the daily
            report', 'active': True, 'oneshot': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ValidationError
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
        )
    ).parsed
