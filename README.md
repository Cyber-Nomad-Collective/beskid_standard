# corelib

This directory is the compiler-pinned core library source (submodule repository: `beskid_standard`).

## Canonical source paths

- `compiler/corelib/beskid_corelib` from the superrepo root (`corelib/beskid_corelib` inside the compiler repo).

Compiler tooling and tests use this canonical path, with `beskid_corelib` naming enforced in `Project.proj`.

## Project identity

- Canonical source directory remains `compiler/corelib/beskid_corelib/` in aggregate workspaces.
- `Project.proj` `project.name` is `corelib`.
- Release packaging publishes this project to pckg under package identity `corelib`.

## CI/CD authority

`beskid_standard` is the publish authority for corelib artifacts.

- Standalone CI/Nox live in this repository:
  - `.github/workflows/ci.yml`
  - `noxfile.py`
  - `ci/version.py`
  - `ci/publish_corelib.py`
- Required secret in this repository: `BESKID_PCKG_KEY` (workflow maps to `BESKID_PCKG_API_KEY`).
- Publish workflow checks out `beskid_compiler`, builds `beskid_cli`, runs `beskid pckg pack` + `beskid pckg upload` with `BESKID_CLI_BIN` (falls back to downloading a release binary only when `BESKID_CLI_BIN` is unset, for example locally).

## Public documentation

Canonical prose lives next to the sources in **`beskid_corelib/docs/`** (packed as `docs/**/*.md`). The docs site Starlight section at `site/website/src/content/docs/corelib/` holds short pages that link to those files. Generated CLI docs from `beskid doc` / `beskid pckg pack` land under **`.beskid/docs/`** in the package tree when present.

## Local verification

From this repository root:

```bash
python -m nox --non-interactive -s quality
```
