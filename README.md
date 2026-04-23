# corelib

This directory is the compiler-pinned core library source (submodule repository: `beskid_standard`).

## Canonical source paths

- `corelib/beskid_corelib`.

Compiler tooling and tests use this canonical path, with `beskid_corelib` naming enforced in `Project.proj`.

## Project identity

- `Project.proj` `project.name` must be `beskid_corelib`.
- Release packaging publishes this project as package `beskid_corelib` to pckg.

## CI/CD authority

`beskid_standard` is the publish authority for corelib artifacts.

- Standalone CI/Nox live in this repository:
  - `.github/workflows/ci.yml`
  - `noxfile.py`
  - `ci/version.py`
  - `ci/publish_corelib.py`
- Required secret in this repository: `BESKID_PCKG_KEY` (workflow maps to `BESKID_PCKG_API_KEY`).
- Publish workflow installs/downloads the Beskid CLI and runs `beskid pckg pack` + `beskid pckg upload`.

## Local verification

From this repository root:

```bash
python -m nox --non-interactive -s quality
```
