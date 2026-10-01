# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Introduction

`alfasim-sdk` is the public API/SDK of ALFAsim: the `.alfacase` format and its
`*Description` classes (`_internal/alfacase/case_description.py`), the plugin hook specs
(pluggy, `hookimpl`), the C/C++ solver API headers (`alfasim_sdk_api/`), unit categories,
and a result reader. Everything public is re-exported from `alfasim_sdk/__init__.py`;
`_internal` is private.

## Build / test

Inside ESSS there is no separate environment: activate the `alfasim` app environment (or this
repo's pixi-devenv env), then run `pre-commit install` once.

- Tests: `pytest` (single test: `pytest tests/path/test_x.py::test_name`).
- Type-check: `mypy`.
- After changing any `*Description` class, run `inv cog` to regenerate the cogged sections
  of `case_description.py`, `schema.py` and `docs/source/alfacase_definitions/`, and commit
  the result. CI runs `inv cog --check` and fails on stale generated files.
- Docs: `inv docs`.

## Changes go through PRs

Never push to `master`. Branch as `fb-<PROJECT-KEY>-<ISSUE>-<name>` (use `mu checkout -b`
from the app repo, since the branch must span the whole repo group) and open a PR on
`ESSS/alfasim-sdk` following `.github/PULL_REQUEST_TEMPLATE.md`. For user-facing changes:

- Add an entry to the `UNRELEASED` section of `CHANGELOG.rst` (create it if missing).
- Check `__version__` in `src/alfasim_sdk/_internal/version.py`. If it is a released version
  (e.g. `1.6.0`), bump it to the next minor with a `.dev` suffix (`1.7.0.dev`). If it already
  ends in `.dev`, an earlier change already did that since the last release, so leave it
  alone. Releases themselves follow `RELEASING.rst`.

## API, downstream usage and the changelog

This package is consumed downstream by the ALFAsim application (which reads/writes
`.alfacase` files and implements the hooks and solver API) and by every
`alfasim-plugin-*` repo (which implement hooks and call the solver API), as well as by
external users and plugin authors. Any change to a public name, `*Description` attribute,
enum member, hook spec, unit category or C API function is therefore a downstream change,
and usually requires matching changes in the app and/or plugins.

**Every API/downstream change must be clearly identified in `CHANGELOG.rst`** under the
`UNRELEASED` section, naming the exact classes/attributes/functions affected. **Breaking
changes** (removals, renames, changed types/defaults/semantics, removed enum members) must be
prefixed with `**Breaking Change**:` and state what users should use instead.

### What counts as a breaking change here

A change is breaking if existing `.alfacase` files, Python code using the SDK, or compiled
plugins stop working or silently behave differently. In particular:

- **`.alfacase` / `*Description`:** removing or renaming an attribute, class or enum member,
  changing an enum's serialized value, changing an attribute's type or structure (e.g. a
  scalar becoming a dict), or changing a default value (old files load fine but simulate
  differently). Whenever old files would fail to load, also add a migration function to
  `_internal/alfacase/migration.py` so they keep loading.
- **Plugin hooks:** changing a hook's signature or return semantics, or adding a hook that
  plugins are required to implement.
- **C/C++ solver API (`alfasim_sdk_api/`):** changing a function's signature, a struct or
  enum layout, or error codes, which breaks plugins compiled against the previous headers.
- **Units:** removing a unit category or restricting the units allowed in one.
- **Python API:** removing or renaming anything exported from `alfasim_sdk`, or changing
  signatures/return types (e.g. in `result_reader`).

Purely additive changes (a new optional attribute with a backward-compatible default, a new
enum member, a new optional hook or API function) are not breaking, but still go in the
changelog.
