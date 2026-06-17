# Changelog

## 0.3.0

- `KarakeepClient.async_get_version` now treats the optional version endpoint
  as unavailable and returns `None` for any non-JSON, error, or unexpected
  response instead of raising, so servers older than `0.29.0` no longer cause
  an error.

## 0.2.0

- `KarakeepClient.async_get_stats` now returns a typed `KarakeepStats` dataclass
  instead of a raw `dict`.
- Validate stats counts in the library and raise `KarakeepInvalidResponseError`
  for missing or non-integer values.

## 0.1.0

- Initial release.
- Add async `KarakeepClient` with injected `aiohttp.ClientSession`.
- Support stats, health, and version endpoints.
- Add typed exceptions for authentication, connection, timeout, API, and invalid
  response failures.
