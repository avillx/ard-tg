from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_session_body import CreateSessionBody
from ...models.create_session_response_200 import CreateSessionResponse200
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: CreateSessionBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/session",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> CreateSessionResponse200 | Error | ValidationError | None:
    if response.status_code == 200:
        response_200 = CreateSessionResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:

        def _parse_response_400(data: object) -> Error | ValidationError:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_400_type_0 = Error.from_dict(data)

                return response_400_type_0
            except TypeError, ValueError, AttributeError, KeyError:
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_400_type_1 = ValidationError.from_dict(data)

            return response_400_type_1

        response_400 = _parse_response_400(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Response[CreateSessionResponse200 | Error | ValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody,
) -> Response[CreateSessionResponse200 | Error | ValidationError]:
    """Create a new session

     Creates a new session bound to a profile. A session holds the conversation
    history, token usage, and metadata.

    Args:
        body (CreateSessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse200 | Error | ValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody,
) -> CreateSessionResponse200 | Error | ValidationError | None:
    """Create a new session

     Creates a new session bound to a profile. A session holds the conversation
    history, token usage, and metadata.

    Args:
        body (CreateSessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse200 | Error | ValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody,
) -> Response[CreateSessionResponse200 | Error | ValidationError]:
    """Create a new session

     Creates a new session bound to a profile. A session holds the conversation
    history, token usage, and metadata.

    Args:
        body (CreateSessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSessionResponse200 | Error | ValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSessionBody,
) -> CreateSessionResponse200 | Error | ValidationError | None:
    """Create a new session

     Creates a new session bound to a profile. A session holds the conversation
    history, token usage, and metadata.

    Args:
        body (CreateSessionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSessionResponse200 | Error | ValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
