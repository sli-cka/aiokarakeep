"""Tests for aiokarakeep."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from aiohttp import ClientConnectionError

import aiokarakeep
from aiokarakeep import (
    KarakeepApiError,
    KarakeepAuthError,
    KarakeepClient,
    KarakeepConnectionError,
    KarakeepError,
    KarakeepInvalidResponseError,
    KarakeepStats,
    KarakeepTimeoutError,
)

STATS_PAYLOAD = {
    "numBookmarks": 10,
    "numFavorites": 2,
    "numArchived": 3,
    "numHighlights": 4,
    "numLists": 5,
    "numTags": 6,
}


class FakeResponse:
    """Minimal aiohttp response double."""

    def __init__(
        self,
        status: int,
        payload: Any = None,
        *,
        json_error: Exception | None = None,
    ) -> None:
        """Initialize fake response."""
        self.status = status
        self._payload = payload
        self._json_error = json_error

    async def json(self) -> Any:
        """Return JSON payload or raise the configured error."""
        if self._json_error is not None:
            raise self._json_error
        return self._payload


class FakeRequestContext:
    """Minimal aiohttp request context double."""

    def __init__(self, response: FakeResponse | Exception) -> None:
        """Initialize fake request context."""
        self._response = response

    async def __aenter__(self) -> FakeResponse:
        """Enter the request context."""
        if isinstance(self._response, Exception):
            raise self._response
        return self._response

    async def __aexit__(self, *args: object) -> None:
        """Exit the request context."""


class FakeSession:
    """Minimal aiohttp session double."""

    def __init__(self, response: FakeResponse | Exception) -> None:
        """Initialize fake session."""
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: Any) -> FakeRequestContext:
        """Return the fake response."""
        self.calls.append({"url": url, **kwargs})
        return FakeRequestContext(self.response)


def test_public_exports() -> None:
    """Test the supported public package exports."""
    assert set(aiokarakeep.__all__) == {
        "KarakeepApiError",
        "KarakeepAuthError",
        "KarakeepClient",
        "KarakeepConnectionError",
        "KarakeepError",
        "KarakeepInvalidResponseError",
        "KarakeepStats",
        "KarakeepTimeoutError",
    }
    assert issubclass(KarakeepAuthError, KarakeepApiError)
    assert issubclass(KarakeepTimeoutError, KarakeepConnectionError)
    assert issubclass(KarakeepConnectionError, KarakeepError)


@pytest.mark.asyncio
async def test_get_stats() -> None:
    """Test fetching Karakeep stats."""
    session = FakeSession(FakeResponse(200, STATS_PAYLOAD))
    client = KarakeepClient("https://karakeep.example.com/", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_stats() == KarakeepStats(
        num_bookmarks=10,
        num_favorites=2,
        num_archived=3,
        num_highlights=4,
        num_lists=5,
        num_tags=6,
    )
    assert (
        session.calls[0]["url"]
        == "https://karakeep.example.com/api/v1/users/me/stats"
    )
    assert session.calls[0]["headers"] == {"Authorization": "Bearer token"}
    assert session.calls[0]["timeout"].total == 15


@pytest.mark.asyncio
async def test_custom_timeout() -> None:
    """Test requests use the configured timeout."""
    session = FakeSession(FakeResponse(200, STATS_PAYLOAD))
    client = KarakeepClient(
        "https://karakeep.example.com",
        "token",
        session,  # type: ignore[arg-type]
        timeout=30,
    )

    await client.async_get_stats()

    assert session.calls[0]["timeout"].total == 30


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [401, 403])
async def test_get_stats_auth_error(status: int) -> None:
    """Test auth errors are mapped to KarakeepAuthError."""
    session = FakeSession(FakeResponse(status, {"error": "unauthorized"}))
    client = KarakeepClient("https://karakeep.example.com", "bad-token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepAuthError) as exc_info:
        await client.async_get_stats()

    assert exc_info.value.status == status


@pytest.mark.asyncio
async def test_get_stats_api_error() -> None:
    """Test non-auth HTTP errors are mapped to KarakeepApiError."""
    session = FakeSession(FakeResponse(500, {"error": "server"}))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepApiError) as exc_info:
        await client.async_get_stats()

    assert exc_info.value.status == 500


@pytest.mark.asyncio
async def test_get_stats_connection_error() -> None:
    """Test connection errors are mapped to KarakeepConnectionError."""
    session = FakeSession(ClientConnectionError("boom"))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepConnectionError):
        await client.async_get_stats()


@pytest.mark.asyncio
async def test_get_stats_timeout() -> None:
    """Test timeouts are mapped to KarakeepTimeoutError."""
    session = FakeSession(asyncio.TimeoutError())
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepTimeoutError):
        await client.async_get_stats()


@pytest.mark.asyncio
async def test_get_stats_invalid_json() -> None:
    """Test invalid JSON is mapped to KarakeepInvalidResponseError."""
    session = FakeSession(FakeResponse(200, json_error=ValueError("invalid json")))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepInvalidResponseError):
        await client.async_get_stats()


@pytest.mark.asyncio
async def test_get_stats_invalid_payload() -> None:
    """Test non-object stats payloads are rejected."""
    session = FakeSession(FakeResponse(200, ["not", "an", "object"]))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepInvalidResponseError):
        await client.async_get_stats()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {k: v for k, v in STATS_PAYLOAD.items() if k != "numBookmarks"},
        {**STATS_PAYLOAD, "numBookmarks": "10"},
        {**STATS_PAYLOAD, "numBookmarks": None},
        {**STATS_PAYLOAD, "numBookmarks": True},
    ],
)
async def test_get_stats_invalid_counts(payload: dict[str, Any]) -> None:
    """Test missing or non-integer stat counts are rejected."""
    session = FakeSession(FakeResponse(200, payload))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepInvalidResponseError):
        await client.async_get_stats()


@pytest.mark.asyncio
async def test_get_health() -> None:
    """Test fetching health status."""
    session = FakeSession(FakeResponse(200, {"status": "ok"}))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_health() == {"status": "ok", "status_code": 200}


@pytest.mark.asyncio
async def test_get_health_non_json() -> None:
    """Test health handles non-JSON responses."""
    session = FakeSession(FakeResponse(200, json_error=ValueError("invalid json")))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_health() == {"status": "unknown", "status_code": 200}


@pytest.mark.asyncio
async def test_get_health_non_object_payload() -> None:
    """Test health handles JSON responses that are not objects."""
    session = FakeSession(FakeResponse(200, ["ok"]))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_health() == {"status": "unknown", "status_code": 200}


@pytest.mark.asyncio
async def test_get_version() -> None:
    """Test fetching Karakeep version."""
    session = FakeSession(FakeResponse(200, {"version": "0.29.0"}))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_version() == "0.29.0"


@pytest.mark.asyncio
async def test_get_version_404() -> None:
    """Test missing version endpoint returns None."""
    session = FakeSession(FakeResponse(404, {"error": "not found"}))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    assert await client.async_get_version() is None


@pytest.mark.asyncio
async def test_get_version_invalid_payload() -> None:
    """Test version rejects non-object responses."""
    session = FakeSession(FakeResponse(200, ["0.29.0"]))
    client = KarakeepClient("https://karakeep.example.com", "token", session)  # type: ignore[arg-type]

    with pytest.raises(KarakeepInvalidResponseError):
        await client.async_get_version()
