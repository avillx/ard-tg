from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_task_response_404 import PatchTaskResponse404
from ...models.task_patch import TaskPatch
from ...models.validation_error import ValidationError
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


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | PatchTaskResponse404 | ValidationError | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = ValidationError.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = PatchTaskResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | PatchTaskResponse404 | ValidationError]:
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
) -> Response[Any | PatchTaskResponse404 | ValidationError]:
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
        Response[Any | PatchTaskResponse404 | ValidationError]
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
) -> Any | PatchTaskResponse404 | ValidationError | None:
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
        Any | PatchTaskResponse404 | ValidationError
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
) -> Response[Any | PatchTaskResponse404 | ValidationError]:
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
        Response[Any | PatchTaskResponse404 | ValidationError]
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
) -> Any | PatchTaskResponse404 | ValidationError | None:
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
        Any | PatchTaskResponse404 | ValidationError
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
        )
    ).parsed
