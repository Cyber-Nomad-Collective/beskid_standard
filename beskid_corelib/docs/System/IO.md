`System.IO` implements **`Print`** and **`PrintLine`** using
**`System.Syscall.WriteWith`** and typed descriptor selection
(`Descriptor::Standard(StandardStream::Stdout)`). Failures from `WriteWith`
trigger **`__panic_str("System.IO.Print failed")`**—there is no alternate silent path.

## Functions

| Function | Behavior |
|----------|----------|
| `Print(string text)` | Writes UTF-8 `text` to stdout (no newline). |
| `PrintLine(string text)` | **`Print(text)`** then **`Print("\n")`** (newline is a literal string in source). |

## Contract

- Encoding follows the language **`string`** representation (UTF-8 bytes at the syscall boundary).
- Line endings are corelib policy (`"\n"`), not a separate runtime builtin.
