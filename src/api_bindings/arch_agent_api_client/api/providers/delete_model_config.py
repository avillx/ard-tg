from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.message import Message
from ...types import Response


def _get_kwargs(
    name: str,
    model: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/providers/{name}/models/{model}".format(
            name=quote(str(name), safe=""),
            model=quote(str(model), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | Message | None:
    if response.status_code == 200:
        response_200 = Message.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

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
    model: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Message]:
    """Delete a model configuration

     Deletes a model configuration. The model name in the path is base64url-encoded.

    Args:
        name (str):
        model (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
    """

    kwargs = _get_kwargs(
        name=name,
        model=model,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Message | None:
    """Delete a model configuration

     Deletes a model configuration. The model name in the path is base64url-encoded.

    Args:
        name (str):
        model (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
    """

    return sync_detailed(
        name=name,
        model=model,
        client=client,
    ).parsed


async def asyncio_detailed(
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Message]:
    """Delete a model configuration

     Deletes a model configuration. The model name in the path is base64url-encoded.

    Args:
        name (str):
        model (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Message]
    """

    kwargs = _get_kwargs(
        name=name,
        model=model,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Message | None:
    """Delete a model configuration

     Deletes a model configuration. The model name in the path is base64url-encoded.

    Args:
        name (str):
        model (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Message
    """

    return (
        await asyncio_detailed(
            name=name,
            model=model,
            client=client,
        )
    ).parsed
