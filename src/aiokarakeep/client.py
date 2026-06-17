"""Client for the Karakeep API."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import (
    ClientConnectionError,
    ClientError,
    ClientSession,
    ClientTimeout,
    ContentTypeError,
    ServerTimeoutError,
)

from .exceptions import (
    KarakeepApiError,
    KarakeepAuthError,
    KarakeepConnectionError,
    KarakeepInvalidResponseError,
    KarakeepTimeoutError,
)
from .models import KarakeepStats

DEFAULT_TIMEOUT = 15


class KarakeepClient:
    """Async client for the Karakeep API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        session: ClientSession,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Karakeep API client."""
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._session = session
        self._timeout = ClientTimeout(total=timeout)

    @property
    def base_url(self) -> str:
        """Return the normalized Karakeep base URL."""
        return self._base_url

    @property
    def session(self) -> ClientSession:
        """Return the injected aiohttp client session."""
        return self._session

    @property
    def _headers(self) -> dict[str, str]:
        """Return request headers."""
        return {"Authorization": f"Bearer {self._token}"}

    async def async_get_stats(self) -> KarakeepStats:
        """Return statistics for the authenticated Karakeep user."""
        _, data = await self._async_request_json("/api/v1/users/me/stats")
        if not isinstance(data, dict):
            raise KarakeepInvalidResponseError("Stats response is not an object")
        return KarakeepStats.from_dict(data)

    async def async_get_health(self) -> dict[str, Any]:
        """Return Karakeep health information."""
        status_code, data = await self._async_request_json(
            "/api/health",
            raise_for_status=False,
            allow_invalid_json=True,
        )

        if not isinstance(data, dict):
            data = {"status": "unknown"}

        return {**data, "status_code": status_code}

    async def async_get_version(self) -> str | None:
        """Return the Karakeep version, if exposed by the server.

        The version endpoint is optional and only available on Karakeep
        ``0.29.0`` and later. Any response that does not contain a valid
        version string (missing endpoint, non-JSON body, or unexpected status
        code) is treated as unknown and returns ``None``. Only connection and
        timeout errors are raised.
        """
        status_code, data = await self._async_request_json(
            "/api/version",
            raise_for_status=False,
            allow_invalid_json=True,
        )
        if status_code >= 400 or not isinstance(data, dict):
            return None

        version = data.get("version")
        return version if isinstance(version, str) else None

    async def _async_request_json(
        self,
        path: str,
        *,
        raise_for_status: bool = True,
        allow_invalid_json: bool = False,
    ) -> tuple[int, Any]:
        """Request JSON from the Karakeep API."""
        url = f"{self._base_url}{path}"

        try:
            async with self._session.get(
                url,
                headers=self._headers,
                timeout=self._timeout,
            ) as response:
                status_code = response.status
                if raise_for_status:
                    self._raise_for_status(status_code)

                try:
                    data = await response.json()
                except (ContentTypeError, ValueError) as err:
                    if allow_invalid_json:
                        data = None
                    else:
                        raise KarakeepInvalidResponseError(
                            "Response is not valid JSON"
                        ) from err

                return status_code, data
        except (asyncio.TimeoutError, ServerTimeoutError, TimeoutError) as err:
            raise KarakeepTimeoutError("Timed out connecting to Karakeep") from err
        except ClientConnectionError as err:
            raise KarakeepConnectionError("Could not connect to Karakeep") from err
        except ClientError as err:
            raise KarakeepApiError("Error communicating with Karakeep") from err

    def _raise_for_status(self, status: int) -> None:
        """Raise a typed exception for unsuccessful HTTP responses."""
        if status < 400:
            return

        if status in (401, 403):
            raise KarakeepAuthError("Invalid Karakeep API token", status)

        raise KarakeepApiError(
            f"Karakeep API returned HTTP status {status}",
            status,
        )
