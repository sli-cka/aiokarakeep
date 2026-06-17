# Changelog

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
