"""Exceptions for aiokarakeep."""

from __future__ import annotations


class KarakeepError(Exception):
    """Base exception for aiokarakeep."""


class KarakeepApiError(KarakeepError):
    """Raised when the Karakeep API returns an error."""

    def __init__(self, message: str, status: int | None = None) -> None:
        """Initialize the API error."""
        super().__init__(message)
        self.status = status


class KarakeepAuthError(KarakeepApiError):
    """Raised when Karakeep rejects the configured API token."""


class KarakeepConnectionError(KarakeepError):
    """Raised when Karakeep cannot be reached."""


class KarakeepTimeoutError(KarakeepConnectionError):
    """Raised when a Karakeep request times out."""


class KarakeepInvalidResponseError(KarakeepError):
    """Raised when Karakeep returns an unexpected response body."""

