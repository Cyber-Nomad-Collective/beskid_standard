# Core.Text.Number

`Core.Text.Number` parses and formats numbers in plain Beskid and converts `f64` to `i64` with explicit failures. Errors are `Core.Text.NumberError`:

| Variant | Meaning |
|---------|---------|
| `Empty` | No digits. |
| `InvalidCharacter(offset)` | Byte at `offset` is not valid there. |
| `Overflow` | Value does not fit. |
| `NotFinite` | NaN or infinity cannot become an integer. |

## Parsing

| Function | Accepts |
|----------|---------|
| `ParseI64(text)` | Optional `+`/`-`, decimal digits, the full `i64` range. No whitespace. |
| `ParseHex(text)` | Optional `0x`/`0X`, hex digits, up to `2^63 - 1`. |
| `DigitsAt(text, at, count, radix)` | Exactly `count` digits in base `radix` (2 to 16) at offset `at`, as an `i64`, or `-1`. Reads fixed-width fields such as `\uXXXX` escapes, RFC 3339 date parts, and `#rrggbb` colors. |
| `ParseF64(text)` | Optional sign, digits with optional fraction (`.5` and `3.` allowed), optional `e`/`E` exponent. Rejects `nan` and `inf`. |

```beskid
use Core.Text.Number;

i64 port = match Number.ParseI64(input) {
    Result::Ok(value) => value,
    Result::Error(_) => 8080_i64,
};
```

## Formatting

| Function | Output |
|----------|--------|
| `FormatFixed(value, decimals)` | Exactly `decimals` (0-15) fraction digits, half away from zero: `FormatFixed(3.14159, 2) == "3.14"`. |
| `FormatGeneral(value)` | Up to 15 significant digits; plain notation for magnitudes in `[1e-5, 1e15)`, otherwise `1e+15` style. Integral values have no fraction. |
| `FormatHex(value)` | Lowercase hex without prefix; negatives print 16 two's-complement digits. |

NaN prints `NaN`; infinities print `Infinity` and `-Infinity`. Decimal `i64` formatting is plain interpolation: `"${value}"`.

## Conversion

| Function | Behavior |
|----------|----------|
| `TruncateToI64(value)` | Toward zero; `NotFinite` or `Overflow` outside `[-2^63, 2^63)`. |
| `RoundToI64(value)` | Half away from zero, same failures. |
| `IsFinite(value)` | Neither NaN nor infinite. |
| `Pow10(exponent)` | `10^exponent` as f64. |
| `MinI64()` / `MaxI64()` | Range limits. |

The 0.5.2 compiler cannot lower an `i64(f64)` cast, so these functions decompose the value bit by bit instead.

## Precision

`ParseF64` and the formatters are accurate to about 15 significant digits but are not correctly rounded, so a text round trip of an arbitrary double can differ in the last digit.
