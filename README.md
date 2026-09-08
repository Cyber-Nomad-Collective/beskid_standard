# corelib

This directory is the compiler-pinned core library source (submodule repository: `beskid_standard`).

## Licensing

The core library is Apache-2.0. It may be compiled into user programs without
controlling the license of user-authored code; distributors retain the
applicable Apache license and notices. See [LICENSING.md](LICENSING.md).

## Canonical source paths

- Workspace root: `compiler/corelib/` (`CoreLib.bws`, `packages/`, `beskid_corelib/`).
- Published / CLI-embedded package: `compiler/corelib/beskid_corelib` (`name = corelib`, `type = Aggregate`) with path dependencies on `packages/foundation`, `packages/runtime`, `packages/console`, `packages/concurrency`, and `packages/compiler-sdk`.
- **Mod SDK:** depend on `corelib_compiler_sdk` and import from `Beskid.Compiler.*` explicitly (see `packages/compiler-sdk/README.md`).
- **Mod SDK `.bd` regeneration:** from the parent compiler workspace, run `./corelib/packages/compiler-sdk/regen_mod_sdk_surfaces.sh` after editing reflected `beskid_analysis` sources.

Compiler tooling discovers `compiler/corelib/beskid_corelib/corelib.bproj`; the parent workspace manifest is `CoreLib.bws`.

## Project identity

- Canonical aggregate package directory remains `compiler/corelib/beskid_corelib/`.
- `corelib.bproj` declares `name = corelib` and `type = Aggregate` (dependency-only, no `src/`); sibling packages use `corelib_foundation`, `corelib_runtime`, and `corelib_compiler_sdk` internally.
- Release packaging classifies the workspace explicitly: the eight production
  packages are packed as canonical `.bpk` artifacts and published one at a time
  through `POST /api/packages/{name}/versions`; development and test-only
  members are rejected from the publication inventory. The same superrepo lane
  publishes all seven first-party templates after every artifact has validated.

## CI/CD authority

The initialized `beskid_standard` checkout is the source authority; the
superrepo workflow is the publication authority for corelib artifacts.

- Superrepo workflow [`.github/workflows/corelib.yml`](../../.github/workflows/corelib.yml)
  runs the native corelib gate and the fail-closed
  [`scripts/ci/corelib-publish.sh`](../../scripts/ci/corelib-publish.sh) publisher.
- From an initialized superrepo checkout, `bash scripts/ci/corelib-publish.sh
  0.4.0 --dry-run` builds and validates the complete 15-artifact publication set
  without credentials or registry mutation.
- Local fast path: from parent compiler workspace, `just corelib` runs all `corelib_tests` targets via release `beskid_cli`.
