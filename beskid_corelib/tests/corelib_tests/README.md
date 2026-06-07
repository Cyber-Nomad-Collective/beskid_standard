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
| System I/O | `use System.Input;`, `use System.Error;`, `use System.FS;`, `use System.Path;` |
| Collections | `use Collections.Array;`, `use Collections.List;`, … |
| Core bytes | `use Core.Bytes;` |

## Normalizing imports

From `compiler/`:

```bash
python3 corelib/ci/normalize_corelib_test_imports.py
python3 corelib/ci/normalize_corelib_test_imports.py --check  # CI drift guard
```

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
