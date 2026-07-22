from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.message import Message
from ...models.task_patch import TaskPatch
from ...types import Response


def _get_kwargs(
    name: str,
    *,
    body: TaskPatch,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/task/{name}".format(
            name=quote(str(name), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | Message | None:
    if response.status_code == 200:
        response_200 = Message.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | Message]:
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
    body: TaskPatch,
) -> Response[Error | Message]:
    """Patch a task

     Partially updates a task. Only the supplied fields are updated.
    Fields set to `null` are ignored. To deactivate a task, set `active` to `false`.

    Args:
        name (str):
        body (TaskPatch): Partial update for a task. Only supplied fields are updated. Fields set
            to `null` are ignored. Example: {'active': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
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
    body: TaskPatch,
) -> Error | Message | None:
    """Patch a task

     Partially updates a task. Only the supplied fields are updated.
    Fields set to `null` are ignored. To deactivate a task, set `active` to `false`.

    Args:
        name (str):
        body (TaskPatch): Partial update for a task. Only supplied fields are updated. Fields set
            to `null` are ignored. Example: {'active': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
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
    body: TaskPatch,
) -> Response[Error | Message]:
    """Patch a task

     Partially updates a task. Only the supplied fields are updated.
    Fields set to `null` are ignored. To deactivate a task, set `active` to `false`.

    Args:
        name (str):
        body (TaskPatch): Partial update for a task. Only supplied fields are updated. Fields set
            to `null` are ignored. Example: {'active': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
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
    body: TaskPatch,
) -> Error | Message | None:
    """Patch a task

     Partially updates a task. Only the supplied fields are updated.
    Fields set to `null` are ignored. To deactivate a task, set `active` to `false`.

    Args:
        name (str):
        body (TaskPatch): Partial update for a task. Only supplied fields are updated. Fields set
            to `null` are ignored. Example: {'active': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
        )
    ).parsed
