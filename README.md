# corelib

This directory is the compiler-pinned core library source (submodule repository: `beskid_standard`).

## Canonical source paths

- Workspace root: `compiler/corelib/` (`Workspace.proj`, `packages/`, `beskid_corelib/`).
- Published / CLI-embedded package: `compiler/corelib/beskid_corelib` (`project.name = corelib`) with path dependencies on `packages/foundation`, `packages/runtime`, and `packages/compiler-sdk` (Mod SDK `Beskid.Compiler.*` typed surfaces; syntax AST nodes live under `packages/compiler-sdk/src/Beskid/Compiler/Syntax/Nodes/`).
- **Gap:** the aggregate `Prelude.bd` intentionally does **not** re-export `Beskid.Compiler.*` yet; including those `pub mod` lines in the prelude triggers a stack overflow in the reference semantic pipeline when combined with the rest of the prelude. Depend on `corelib_compiler_sdk` and import from `Beskid.Compiler.*` (see `packages/compiler-sdk/src/Prelude.bd`) until the compiler rule pipeline is fixed.
- **Mod SDK `.bd` regeneration:** from the parent compiler workspace, run `./corelib/packages/compiler-sdk/regen_mod_sdk_surfaces.sh` after editing reflected `beskid_analysis` sources (see `packages/compiler-sdk/README.md`).

Compiler tooling discovers `corelib/beskid_corelib/Project.proj`; the parent workspace supplies resolver policy and future multi-member orchestration.

## Project identity

- Canonical aggregate package directory remains `compiler/corelib/beskid_corelib/`.
- `Project.proj` `project.name` is `corelib` for the aggregate lib; sibling packages use `corelib_foundation`, `corelib_runtime`, and `corelib_compiler_sdk` internally.
- Release packaging upserts and publishes **every workspace member** to pckg (`corelib`, `corelib_foundation`, `corelib_runtime`, `corelib_compiler_sdk`, `corelib_console`, `corelib_concurrency`) via `POST /api/workspaces/publish` driven by centralized superrepo Dagger CI.

## CI/CD authority

Corelib publish is centralized in the superrepo workflows and shared Dagger module:

- superrepo workflows under `.github/workflows/`
- shared Dagger module under `beskid_infra/dagger/`

## Public documentation

Canonical prose lives next to the sources in **`beskid_corelib/docs/`** (packed as `docs/**/*.md`). The docs site Starlight section at `site/website/src/content/docs/corelib/` holds short pages that link to those files. Generated CLI docs from `beskid doc` / `beskid pckg pack` land under **`.beskid/docs/`** in the package tree when present.

## Local verification

Use compiler workspace Cargo tests and the centralized Dagger CI functions.
