# Core.Text.Toml

TOML 1.0 documents parsed into `Toml.TomlValue`:

```beskid
pub enum TomlValue {
    Text(string value),
    Integer(i64 value),
    Float(f64 value),
    Bool(bool value),
    DateTime(string value),
    List(TomlValue[] items),
    Table(string[] keys, TomlValue[] values),
}
```

`Parse(text)` supports comments; bare, quoted, and dotted keys; `[table]` and `[[array.of.tables]]`; basic, literal, and multi-line strings with all escapes and line-ending backslashes; integers with `_` and `0x`/`0o`/`0b`; floats with `inf`/`nan`; booleans; multi-line arrays; and inline tables. Integers keep full `i64` precision. Dates and times are recognized by shape and kept as text in `DateTime`; they are not validated as calendar values (use `Core.Time.Calendar.ParseInstant` for offset date-times).

Errors (`Toml.TomlError`) carry byte offsets: `UnexpectedCharacter`, `UnexpectedEnd`, `UnterminatedString`, `InvalidEscape`, `InvalidNumber`, `DuplicateKey`, and `InvalidTable` (table redefined, key reused as a table, or nesting deeper than 128).

| Accessor | Returns |
|----------|---------|
| `Get(table, key)`, `GetPath(table, "a.b")` | `Option<TomlValue>`; `GetPath` takes bare dotted keys. |
| `Keys(table)`, `Length(value)`, `At(list, index)` | Document-order keys, sizes, elements. |
| `AsText`, `AsInteger`, `AsFloat`, `AsBool`, `AsDateTime` | Typed payloads as `Option`. |

Not supported: rejecting additions to inline tables after definition, and full calendar validation of dates.
