**Core** modules cover language primitives and OS-facing runtime surfaces.

## Language primitives

| Module | Notes |
|--------|-------|
| [Results](./Results.md) | `Result<T, E>` and `Ok` / `Error` helpers |
| [Error-Handling](./Error-Handling.md) | Panic and error-handling contracts |
| [String](./String.md) | UTF-8 string builtins and helpers |
| [Bytes](./Bytes.md) | `u8[]` slice helpers |
| [Encoding](./Encoding.md) | UTF-8, hex, base64 codecs |
| [Optional](./Optional.md) | `Option<T>` and `Some` / `None` |
| [Number](./Text/Number.md) | Integer and float parsing, formatting, checked f64-to-i64 conversion |
| [Json](./Json.md) | RFC 8259 parse, build, inspect, and serialize |

## OS runtime (foundation)

The narrowest, best-supported path today is **`Core.Syscall`** (fd reads/writes via builtins) and split stream helpers **`Core.Input`**, **`Core.Output`**, and **`Core.Error`**.

Higher-level modules (`FS`, `Path`, `Environment`, `Process`, `Time`, `Threading`) largely expose **types and contracts** with **stub or placeholder** implementations until the runtime grows fuller platform support.

| Module | Notes |
|--------|-------|
| [Syscall](./Syscall.md) | **`Write`**, **`Read`** backed by **`__syscall_write`** / **`__syscall_read`** |
| [Input](./Input.md) | **`Read`**, **`ReadLine`** → stdin via syscall |
| [Output](./Output.md) | **`Write`**, **`WriteLine`** → stdout via syscall |
| [Error](./Error.md) | **`Write`**, **`WriteLine`** → stderr via syscall |
| [FS](./FS.md) | **`FsError`**, **`ReadAllText`**, **`WriteAllText`**, **`Exists`** |
| [Path](./Path.md) | POSIX-oriented path composition helpers and lexical normalization |
| [Time](./Time.md) | **`Instant`**, **`Duration`**, UTC civil types |
| [Calendar](./Calendar.md) | Constant-time date arithmetic, weekdays, RFC 3339 parse and format |
| [Environment](./Environment.md) | Process environment helpers |
| [Process](./Process.md) | Process id, exit, and spawn contracts |

Child types under **`Core/Syscall/`**
(`StandardStream`, `Descriptor`, `ReadLimit`, `SyscallError`, `WriteRequest`, `ReadRequest`)
are available from the aggregate prelude where re-exported.

Terminal styling and controls live in the **`corelib_console`** package (`Console`, `Ansi` modules).

## Deprecated `System.*` shims

`System.Syscall`, `System.Input`, `System.Output`, and related paths remain as one-release forwarding shims in `corelib_runtime` and `corelib_concurrency`. Prefer **`Core.*`** imports for new code.
