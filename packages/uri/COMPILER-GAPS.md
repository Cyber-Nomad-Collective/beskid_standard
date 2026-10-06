
## 2026-10-05, uri: concatenating two empty strings yields a string unequal to ""

Symptom: `mut string a = ""; a = a + ""; a == ""` is false (and Assert.Equal<string>
fails); `String.Len(a)` is 0. `"" + "x"`, `"x" + ""` and `SubSlice(s, i, 0) == ""` behave.
Repro:
```
test t { mut string a = ""; a = a + ""; Assert.True(a == "", "empty"); }
```
Workaround: `Uri.Chars.Cat(a, b)` returns the non-empty operand when one side is empty.

## 2026-10-05, uri/codec: assorted 0.5.2 limits met while writing tests

- `host` is a reserved word: `string host` fails with "expected Identifier or GenericArguments".
  Use another name (`hostName`).
- Member access on a call result inside call arguments (`Assert.Equal<string>(Must(x).scheme, ...)`)
  gives ICE `no ISLE lowering rule or fact for CallExpression`. Bind the call result to a local first.
- A `match` expression used as an operand of `+` inside call arguments gives the same ICE.
- String literals do not support `\n` escapes (parse error); build control bytes with
  `String.FromUtf8CodeUnits([104_u8, 10_u8])`.
- `Core.Output.Write` fails (trap) inside `beskid test`; there is no print debugging in tests.
