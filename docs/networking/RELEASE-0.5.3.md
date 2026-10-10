# Publishing 0.5.3

Runbook derived from the 0.5.2 publication (source: root `origin/main` `.woodpecker/*`,
`scripts/ci/*`, `docs/operations/woodpecker.md`; local 0.5.2 records under `/private/tmp/beskid-v052-*`).
The local root `main` checkout is 162 commits behind `origin/main`; use `origin/main` versions of
the CI scripts.

Steps marked (owner) need the owner: a GitHub push, a credential, a waiver, or a build agent.

1. Corelib: push `claude/net-protocols` to `beskid_standard`; merge to its `main`. (owner: push)
2. Compiler `claude/v0.5.3`: set the `corelib` gitlink to the corelib commit from step 1; commit;
   push and merge to `beskid_compiler` `main` (publication uses `--target <sha>` and the rolling
   tag ancestry compare, so the commit must be on GitHub). (owner: push)
3. Root: update local `main` to `origin/main`; commit the `compiler` gitlink and a CHANGELOG
   entry; push to `beskid` `main`. (owner: push)
4. Gates before pushing: run `scripts/ci/woodpecker-release-gates.sh` (Corelib gate and compiler
   Rust gate) and `release-source-inventory.sh` against the new corelib (new packages under
   `packages/`).
5. Builds: Woodpecker `--var BESKID_TASK=build --var BESKID_RELEASE_VERSION=0.5.3` on `main`, or
   the 0.5.2 approach (hand-built Linux on `beskid-codex-build`, macOS locally, Windows on the AWS
   VM, staged in the handoff layout and checked with `woodpecker-release-evidence.mjs`).
   (owner: macOS and Windows agents online; the Mac has ~5 GiB free, too little for a build)
6. Prepare: `--var BESKID_TASK=release --var BESKID_RELEASE_VERSION=0.5.3
   --var BESKID_BUILD_PIPELINE_NUMBER=<run>`; review the qualified output. (owner: review)
7. Windows installer owner waiver for 0.5.3 bound to the final root sha and the new setup EXE
   sha256 (format: `docs/operations/woodpecker.md`, "Owner-scoped Windows installer test
   waiver"). (owner)
8. Publish from a clean local `main` at the built sha, outside CI:
   `BESKID_MANUAL_PUBLISH=1 BESKID_PUBLISH_RELEASE=1 GH_TOKEN=<contents:write on beskid_compiler,
   write on beskid_homebrew> BESKID_WINDOWS_INSTALLER_OWNER_WAIVER_FILE=<file>
   bash scripts/ci/woodpecker-release.sh <run> 0.5.3` → immutable `cli-v0.5.3`, `lsp-v0.5.3`,
   `v0.5.3`; installers; Homebrew formula; rolling `cli-stable`/`lsp-stable`/`stable`. (owner: token)
9. Optional: pckg publish of corelib (`BESKID_TASK=pckg-publish`,
   `BESKID_COMPILER_RELEASE_VERSION=0.5.3`), editors, blog.
10. Notify the v0.6 session ("Beskid 0.6.0 handoff checkpoint") with the tag so it merges 0.5.3.

Known 0.5.3 release notes inputs: compiler CHANGELOG `[0.5.3]` (per-file corelib authority,
typed CLIF blocks, optional externs, keyword boundaries, opt_level speed, root/barrier elision,
versioned soname linking, trap code 11 → runtime kits must be rebuilt) and corelib CHANGELOG
(networking packages).
