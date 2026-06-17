"""Data models for the Karakeep API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .exceptions import KarakeepInvalidResponseError


def _require_int(data: dict[str, Any], key: str) -> int:
    """Return an integer field from a payload or raise on invalid data."""
    value = data.get(key)
    # bool is a subclass of int but is never a valid count.
    if not isinstance(value, int) or isinstance(value, bool):
        raise KarakeepInvalidResponseError(
            f"Expected integer for stats field {key!r}, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class KarakeepStats:
    """Usage statistics for the authenticated Karakeep user."""

    num_bookmarks: int
    num_favorites: int
    num_archived: int
    num_highlights: int
    num_lists: int
    num_tags: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KarakeepStats:
        """Create a KarakeepStats from a raw stats payload."""
        return cls(
            num_bookmarks=_require_int(data, "numBookmarks"),
            num_favorites=_require_int(data, "numFavorites"),
            num_archived=_require_int(data, "numArchived"),
            num_highlights=_require_int(data, "numHighlights"),
            num_lists=_require_int(data, "numLists"),
            num_tags=_require_int(data, "numTags"),
        )
