# corelib_tests import conventions

Each Lib target entry under `src/` is compiled with **import-closure** assembly: only modules referenced by explicit `use` lines are pulled from the `corelib` path dependency. Prelude re-exports in aggregate `Prelude.bd` are **not** auto-injected.

## Required imports

Every assertion-using entry:

```beskid
use Testing.Assert;
```

Call assertions unqualified after import (`Assert.Equal`, `Assert.True`, …).

When using `Result::Ok` / `Core.Results.*`:

```beskid
use Core.Results;
```

Add one or more **domain** imports for the API under test (examples):

| Area | Typical `use` |
|------|----------------|
| Console formatting | `use Console.Format;` |
| ANSI escape | `use Ansi.Escape;` |
| Terminal platform | `use Platform.Terminal;` |
| Concurrency | `use Concurrency.Channel;`, `use Concurrency.Hub;`, … |
| System I/O | `use Core.Input;`, `use Core.Error;`, `use Core.FS;`, `use Core.Path;` |
| Collections | `use Core.Collections.Array;`, `use Core.Collections.List;`, … |
| Core bytes | `use Core.Bytes;` |

## Normalizing imports

From `compiler/`:

```bash
python3 corelib/ci/normalize_corelib_test_imports.py
python3 corelib/ci/normalize_corelib_test_imports.py --check  # CI drift guard
```

## Source fixtures

Negative namespace and native-only overflow fixtures live under `fixtures/`; see `fixtures/README.md`. They are not ordinary `Lib` targets and must be selected by the compile-fail or installed-runtime fixture harness.

## Running tests

```bash
just corelib
# or single target:
./target/release/beskid_cli test --project corelib/beskid_corelib/tests/corelib_tests --target ConsoleFormatMarkdownTests --plain
```

Filter matrix during development:

```bash
export BESKID_CORELIB_TEST_TARGETS=ConsoleAnsiEscapeTests,ConsoleFormatMarkdownTests
just corelib
```
