# corelib_tests

Integration tests for the `corelib` package. The project path-depends on the aggregate
`beskid_corelib` tree (`path = "../.."`) so tests compile against the same sources as the
library.

## Running

From this directory (or via `cargo run -p beskid_cli -- test --project …` from `compiler/`):

```bash
beskid test
beskid test --target CollectionsArrayTests
```

Requires a `beskid` CLI built from a compiler that skips `obj/` and `tests/` when
materializing path dependencies (see `beskid_analysis` workspace materialization).

## `ENAMETOOLONG` / polluted `obj/`

Older compilers copied `tests/corelib_tests/obj/` into materialized path dependencies,
creating deeply nested paths and `File name too long (os error 63)`.

After upgrading the CLI, remove stale artifact trees once:

```bash
rm -rf obj
# optional: also clear aggregate test output under beskid_corelib
rm -rf ../../tests/corelib_tests/obj ../../obj
```

Then rebuild and reinstall the CLI from `compiler/`:

```bash
cargo build -p beskid_cli --release
```

Re-run `beskid test` from this directory.
