from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.model_config import ModelConfig
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    name: str,
    model: str,
    *,
    body: ModelConfig,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/providers/{name}/models/{model}".format(
            name=quote(str(name), safe=""),
            model=quote(str(model), safe=""),
        ),
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
                response_400_type_0 = Error.from_dict(data)

                return response_400_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_400_type_1 = ValidationError.from_dict(data)

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
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
    body: ModelConfig,
) -> Response[Any | Error | Error | ValidationError]:
    """Set model configuration

     Sets configuration for a model. The model name in the path is base64url-encoded.
    Model configuration is provider-specific and may include settings like
    temperature, max_tokens, and top_p.

    Args:
        name (str):
        model (str):
        body (ModelConfig): Model configuration parameters. Provider-specific settings such as
            `temperature`, `max_tokens`, `top_p`, etc.
             Example: {'temperature': 0.7, 'max_tokens': 4096, 'top_p': 1.0}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Error | ValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        model=model,
        body=body,
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
    body: ModelConfig,
) -> Any | Error | Error | ValidationError | None:
    """Set model configuration

     Sets configuration for a model. The model name in the path is base64url-encoded.
    Model configuration is provider-specific and may include settings like
    temperature, max_tokens, and top_p.

    Args:
        name (str):
        model (str):
        body (ModelConfig): Model configuration parameters. Provider-specific settings such as
            `temperature`, `max_tokens`, `top_p`, etc.
             Example: {'temperature': 0.7, 'max_tokens': 4096, 'top_p': 1.0}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Error | ValidationError
    """

    return sync_detailed(
        name=name,
        model=model,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
    body: ModelConfig,
) -> Response[Any | Error | Error | ValidationError]:
    """Set model configuration

     Sets configuration for a model. The model name in the path is base64url-encoded.
    Model configuration is provider-specific and may include settings like
    temperature, max_tokens, and top_p.

    Args:
        name (str):
        model (str):
        body (ModelConfig): Model configuration parameters. Provider-specific settings such as
            `temperature`, `max_tokens`, `top_p`, etc.
             Example: {'temperature': 0.7, 'max_tokens': 4096, 'top_p': 1.0}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | Error | ValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        model=model,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    model: str,
    *,
    client: AuthenticatedClient | Client,
    body: ModelConfig,
) -> Any | Error | Error | ValidationError | None:
    """Set model configuration

     Sets configuration for a model. The model name in the path is base64url-encoded.
    Model configuration is provider-specific and may include settings like
    temperature, max_tokens, and top_p.

    Args:
        name (str):
        model (str):
        body (ModelConfig): Model configuration parameters. Provider-specific settings such as
            `temperature`, `max_tokens`, `top_p`, etc.
             Example: {'temperature': 0.7, 'max_tokens': 4096, 'top_p': 1.0}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | Error | ValidationError
    """

    return (
        await asyncio_detailed(
            name=name,
            model=model,
            client=client,
            body=body,
        )
    ).parsed
