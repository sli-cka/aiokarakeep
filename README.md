# aiokarakeep

Async Python client for the Karakeep API.

This package is intended to provide the API communication layer for the
Karakeep Home Assistant integration. It accepts an injected `aiohttp`
`ClientSession`, which lets Home Assistant own connection pooling and lifecycle.

## Requirements

- Python 3.11 or newer
- `aiohttp` 3.9 or newer

## Installation

```bash
pip install aiokarakeep
```

## Usage

```python
from aiohttp import ClientSession
from aiokarakeep import KarakeepClient


async with ClientSession() as session:
    client = KarakeepClient(
        base_url="https://karakeep.example.com",
        token="YOUR_API_TOKEN",
        session=session,
    )
    stats = await client.async_get_stats()
```

## API

`KarakeepClient` expects:

- `base_url`: Karakeep instance URL, for example `https://karakeep.example.com`
- `token`: Karakeep API token
- `session`: caller-owned `aiohttp.ClientSession`
- `timeout`: optional request timeout in seconds, defaulting to `15`

Available methods:

- `async_get_stats()` calls `GET /api/v1/users/me/stats` and returns the JSON
  object from Karakeep.
- `async_get_health()` calls `GET /api/health` and returns the JSON object plus
  `status_code`. If the endpoint returns non-JSON content, the method returns
  `{"status": "unknown", "status_code": ...}`.
- `async_get_version()` calls `GET /api/version` and returns the version string,
  or `None` when the endpoint is unavailable or does not expose a version.

## Exceptions

The client maps transport and response failures to typed exceptions:

- `KarakeepAuthError`: Karakeep returned HTTP 401 or 403.
- `KarakeepConnectionError`: Karakeep could not be reached.
- `KarakeepTimeoutError`: the request timed out.
- `KarakeepInvalidResponseError`: Karakeep returned malformed or unexpected
  JSON.
- `KarakeepApiError`: Karakeep returned another HTTP error, or `aiohttp`
  reported a generic client error.

All package exceptions inherit from `KarakeepError`.

## Development

```bash
uv run --extra test pytest -q
```

Build and check release artifacts:

```bash
uv run --extra release python -m build --installer uv
uv run --extra release twine check dist/*
```

See `RELEASE_CHECKLIST.md` before publishing a release to PyPI.
