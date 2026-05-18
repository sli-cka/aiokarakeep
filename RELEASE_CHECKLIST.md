# aiokarakeep Release Checklist

Use this checklist after moving `api_library/aiokarakeep` into its own public
repository.

## One-Time Repository Setup

- Confirm the repository is public and uses the OSI-approved MIT license.
- Enable a public CI workflow that runs the test suite for supported Python
  versions.
- Create a PyPI project for `aiokarakeep`.
- Configure PyPI trusted publishing for the GitHub `Publish` workflow and the
  `pypi` environment.
- Protect the default branch and require CI before merging release changes.

## Before Each Release

- Update `version` in `pyproject.toml`.
- Add release notes to `CHANGELOG.md`.
- Update the README if the public API, supported endpoints, or exceptions
  changed.
- Run the test suite:

  ```bash
  uv run --extra test pytest -q
  ```

- Build the source distribution and wheel:

  ```bash
  uv run --extra release python -m build --installer uv
  ```

- Check package metadata:

  ```bash
  uv run --extra release twine check dist/*
  ```

- Install the built wheel in a clean environment and run tests against it when
  practical.

## Publish

- Commit the release changes.
- Tag the release with the same version as `pyproject.toml`, for example
  `v0.1.0`.
- Publish the GitHub release from that tag.
- Confirm the `Publish` workflow uploads the package to PyPI.

## Home Assistant Core Readiness

- Confirm the PyPI version matches a tagged release in the public repository.
- Confirm the package is async and accepts an injected `aiohttp.ClientSession`.
- Confirm Home Assistant can pin the released package in `manifest.json`.
