# Core.String

`Core.String` is the string hub. Strings are UTF-8; every length, offset, and count in this module is a **byte** (code unit) count, and comparison is ordinal (byte-wise). Import it with `use Core.String;` and call `String.Name(...)`.

The hub forwards to the implementation modules `Core.String.Core` (runtime-backed primitives), `Core.String.Search`, `Core.String.Transform`, and `Core.String.Builder`.

`Core.String.Ascii` holds the byte classes every text module shares, so none keeps a private copy: `IsDigit`, `IsLower`, `IsUpper`, `IsAlpha`, `IsAlphanumeric`, `IsHexDigit`, `HexValue` (`0..=15` or `-1`), `IsWhitespace` (space, tab, CR, LF), `IsIdentifierByte(b, first)`, and the byte case maps `ToLower` and `ToUpper`. Import it with `use Core.String.Ascii;`.

## Inspecting

| Function | Behavior |
|----------|----------|
| `Len(text) -> i64` | UTF-8 byte length. `Len("café")` is 5. |
| `IsEmpty(text) -> bool` | `Len(text) == 0`. |
| `IsBlank(text) -> bool` | Empty or only ASCII space, tab, CR, LF. |
| `ByteAt(text, index) -> u8` | Byte at `index`; out of range traps. |
| `SubSlice(text, start, count) -> string` | `count` bytes from `start`. |

## Searching and comparing

| Function | Behavior |
|----------|----------|
| `Contains(text, needle)` | Substring test; the empty needle matches. |
| `IndexOf(text, needle)` / `IndexOfFrom(text, start, needle)` | First offset or `-1`; the empty needle matches at `start`. |
| `LastIndexOf(text, needle)` | Last offset or `-1`; the empty needle matches at `Len(text)`. |
| `StartsWith(text, prefix)` / `EndsWith(text, suffix)` | Affix tests. |
| `StartsWithAt(text, at, prefix)` | `prefix` occurs at offset `at`; offsets outside `text` never match. The affix tests and `LastIndexOf` use it. |
| `SkipWhitespace(text, at) -> i64` | First offset at or after `at` that is not ASCII whitespace. |
| `Count(text, needle)` | Non-overlapping occurrences; the empty needle counts 0. |
| `Compare(a, b) -> i64` | `-1`, `0`, or `1` in ordinal order; a proper prefix sorts first. |
| `Less(a, b) -> bool` | `Compare(a, b) < 0`. Use it instead of `<`, which strings do not support. |

## Transforming

| Function | Behavior |
|----------|----------|
| `Split(text, separator) -> string[]` | Keeps empty fields: `n` separators give `n + 1` parts. An empty separator returns `[text]`. |
| `Lines(text) -> string[]` | Splits on LF, strips one trailing CR per line, ignores a final newline. |
| `Join(parts, separator)` | Inverse of `Split`. |
| `Replace(text, old, replacement)` | All non-overlapping matches, left to right; an empty `old` is a no-op. |
| `Repeat(text, count)` | Non-positive `count` gives `""`. |
| `PadLeft` / `PadRight(text, width, fill)` | Pads to at least `width` bytes; never truncates. |
| `ToUpperAscii` / `ToLowerAscii` | Maps ASCII letters only; other bytes are unchanged. |
| `Trim` / `TrimStart` / `TrimEnd` | `Trim` strips space, tab, CR; `TrimStart`/`TrimEnd` also strip LF. |
| `RemovePrefix` / `RemoveSuffix` | Removes one affix when present. |
| `Concat(a, b)` | `a + b`, safe for two empty operands (see Gotchas). |
| `FromAscii(code)`, `Newline()`, `Tab()` | One-byte strings; string literals have no `\n` or `\t` escapes. |

## Building

`Core.String.Builder` accumulates UTF-8 bytes and materializes once:

```beskid
use Core.String.Builder;

mut StringBuilder b = Builder.New();
b = b.Append("count=");
b = b.AppendI64(42);
b = b.AppendLine(";");
string text = b.ToString(); // "count=42;\n"
```

Builders are linear values: keep using the returned builder and do not append to an older copy.

## Gotchas

- **Empty-plus-empty concatenation.** In the 0.5.2 runtime, `a + b` where both operands are empty produces an invalid string. Library code routes through `String.Concat`; do the same when both sides can be empty.
- **No `\n` escapes.** Literals support only `\"`, `\\`, and `\${`. Use `String.Newline()`, `String.Tab()`, or `String.FromAscii(code)`.
- **Bytes, not characters.** Offsets can land inside a multi-byte sequence if you compute them yourself; offsets returned by the search functions always start a match.
