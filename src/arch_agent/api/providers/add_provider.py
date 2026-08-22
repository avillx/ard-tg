from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.provider_config import ProviderConfig
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: ProviderConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/providers",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | Error | ValidationError | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:

        def _parse_response_400(data: object) -> Error | ValidationError:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_400_type_0 = ValidationError.from_dict(data)

                return response_400_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_400_type_1 = Error.from_dict(data)

            return response_400_type_1

        response_400 = _parse_response_400(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Error | Error | ValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProviderConfig,
) -> Response[Any | Error | Error | ValidationError]:
    """Add a provider

     Adds a new API provider. The provider must have a unique name, a base URL,
    and an API type. The API key is stored separately via `key_ref`.

    Args:
        body (ProviderConfig): Configuration for an API provider (OpenAI-compatible endpoint).
            Example: {'name': 'openai', 'base_url': 'https://api.openai.com/v1', 'api_type': 'openai',
            'key_ref': 'openai_key', 'models': {'gpt-4': {'temperature': 0.7}}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Error | ValidationError]
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
    body: ProviderConfig,
) -> Any | Error | Error | ValidationError | None:
    """Add a provider

     Adds a new API provider. The provider must have a unique name, a base URL,
    and an API type. The API key is stored separately via `key_ref`.

    Args:
        body (ProviderConfig): Configuration for an API provider (OpenAI-compatible endpoint).
            Example: {'name': 'openai', 'base_url': 'https://api.openai.com/v1', 'api_type': 'openai',
            'key_ref': 'openai_key', 'models': {'gpt-4': {'temperature': 0.7}}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Error | ValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ProviderConfig,
) -> Response[Any | Error | Error | ValidationError]:
    """Add a provider

     Adds a new API provider. The provider must have a unique name, a base URL,
    and an API type. The API key is stored separately via `key_ref`.

    Args:
        body (ProviderConfig): Configuration for an API provider (OpenAI-compatible endpoint).
            Example: {'name': 'openai', 'base_url': 'https://api.openai.com/v1', 'api_type': 'openai',
            'key_ref': 'openai_key', 'models': {'gpt-4': {'temperature': 0.7}}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Error | ValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ProviderConfig,
) -> Any | Error | Error | ValidationError | None:
    """Add a provider

     Adds a new API provider. The provider must have a unique name, a base URL,
    and an API type. The API key is stored separately via `key_ref`.

    Args:
        body (ProviderConfig): Configuration for an API provider (OpenAI-compatible endpoint).
            Example: {'name': 'openai', 'base_url': 'https://api.openai.com/v1', 'api_type': 'openai',
            'key_ref': 'openai_key', 'models': {'gpt-4': {'temperature': 0.7}}}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Error | ValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
