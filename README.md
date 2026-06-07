# corelib

This directory is the compiler-pinned core library source (submodule repository: `beskid_standard`).

## Canonical source paths

- Workspace root: `compiler/corelib/` (`CoreLib.bws`, `packages/`, `beskid_corelib/`).
- Published / CLI-embedded package: `compiler/corelib/beskid_corelib` (`name = corelib`, `type = Aggregate`) with path dependencies on `packages/foundation`, `packages/runtime`, `packages/console`, `packages/concurrency`, and `packages/compiler-sdk`.
- **Mod SDK:** depend on `corelib_compiler_sdk` and import from `Beskid.Compiler.*` explicitly (see `packages/compiler-sdk/README.md`).
- **Mod SDK `.bd` regeneration:** from the parent compiler workspace, run `./corelib/packages/compiler-sdk/regen_mod_sdk_surfaces.sh` after editing reflected `beskid_analysis` sources.

Compiler tooling discovers `compiler/corelib/beskid_corelib/corelib.bproj`; the parent workspace manifest is `CoreLib.bws`.

## Project identity

- Canonical aggregate package directory remains `compiler/corelib/beskid_corelib/`.
- `corelib.bproj` declares `name = corelib` and `type = Aggregate` (dependency-only, no `src/`); sibling packages use `corelib_foundation`, `corelib_runtime`, and `corelib_compiler_sdk` internally.
- Release packaging upserts and publishes **every workspace member** to pckg via `POST /api/workspaces/publish` (member metadata lives in `CoreLib.bws`; see `ci/publish_corelib.py`).

## CI/CD authority

`beskid_standard` is the publish authority for corelib artifacts.

- Standalone CI/Nox live in this repository:
  - `.github/workflows/ci.yml`
  - `noxfile.py`
  - `ci/download_cli.sh` (wraps `https://beskid-lang.org/install.sh`, rolling `cli-latest`)
  - `ci/run_corelib_tests.py` (`beskid test` for every target in `beskid_corelib/tests/corelib_tests`)
  - `ci/version.py`
  - `ci/publish_corelib.py`
