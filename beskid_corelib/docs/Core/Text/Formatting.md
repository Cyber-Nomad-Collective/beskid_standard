# Core.Text.Formatting

`Core.Text.Formatting` declares the contract `Formatting`: a value that has a text form.

```beskid
pub contract Formatting
{
    string Format();
}
```

## Conforming types

| Type | `Format()` gives |
|------|------------------|
| `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `word` | Decimal digits, with `-` for a negative value. |
| `f32`, `f64` | The shortest decimal text that reads back as the same value. |
| `bool` | `true` or `false`. |
| `char` | The character as UTF-8 text. |
| `string` | The text, unchanged. |

The primitive implementations are in `Core/Text/Formatting.bd`. An implementation for a primitive type must be in the source file that declares its contract (E1611 otherwise).

## Use in a generic function

A `where T: Formatting` bound accepts every conforming type, and `value.Format()` calls the implementation of the type the function is specialized for:

```beskid
string Show<T>(T value) where T: Formatting
{
    return value.Format();
}
```

`Testing.Assert.Equal`, `Testing.Assert.NotEqual` and `Testing.Expect.Equal` take this bound and put the text of the expected and the actual value into the failure record.
