# Testing.Expect

`Testing.Expect` complements [Testing.Assert](./Assert.md) with typed expectations whose failure messages include the values involved:

```text
Assertion failed: element 1: expected "c" but was "b" (demo)
```

All helpers take the actual value first and an optional `because` string (pass `""` to omit it).

| Function | Checks |
|----------|--------|
| `EqualI64`, `EqualString`, `EqualBool` | Equality; strings are shown quoted. |
| `NearF64(actual, expected, tolerance, because)` | `|actual - expected| <= tolerance`; NaN never matches. |
| `ContainsText`, `StartsWithText` | Substring and prefix. |
| `EqualI64Array`, `EqualStringArray` | Same length and elements; reports the first differing index. |
| `IsSome<T>`, `IsNone<T>` | `Option` shape. |
| `IsOk<T, E>`, `IsError<T, E>` | `Result` shape. |

The first failed expectation stops the test run, as with `Assert`.
