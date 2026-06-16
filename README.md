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
- Release packaging upserts and publishes **every workspace member** to pckg via `POST /api/workspaces/publish` (see superrepo Dagger `package-publish.publish-corelib`).

## CI/CD authority

`beskid_standard` is the publish authority for corelib artifacts.

- Superrepo workflow [`.github/workflows/corelib.yml`](../../.github/workflows/corelib.yml) runs Dagger `corelib-gate` and `package-publish.publish-corelib` from [`beskid_infra/dagger`](../../beskid_infra/dagger/).
- Local fast path: from parent compiler workspace, `just corelib` runs all `corelib_tests` targets via release `beskid_cli`.
