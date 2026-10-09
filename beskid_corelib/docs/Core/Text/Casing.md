# Core.Text.Casing

`Core.Text.Casing` converts identifier casing conventions: `snake_case`, `PascalCase`, `camelCase`, and prefixed callable names. It operates on ASCII ranges only (not Unicode-aware) and is designed for code generation and tooling.

## Functions

| Function | Signature | Behavior |
|----------|-----------|----------|
| `SnakeToPascal` | `string SnakeToPascal(string snake)` | `lower_run` → `LowerRun`. Underscores mark word boundaries. |
| `ToSnake` | `string ToSnake(string text)` | `LowerRun` or `lowerRun` → `lower_run`. Each uppercase letter after the first character starts a new word. |
| `SnakeToCamel` | `string SnakeToCamel(string snake)` | `lower_run` → `lowerRun`. Same as Pascal but lowercases the first character. |
| `CallableFromSnake` | `string CallableFromSnake(string snake, string prefix)` | `lower_run` with prefix `Parse` → `ParseLowerRun`. |

Byte classes (`IsUpper`, `IsLower`, `IsDigit`, `IsIdentifierByte`, and others) live in `Core.String.Ascii`.

## Conversion examples

```beskid
Casing.SnakeToPascal("parse_lower_run");
// → "ParseLowerRun"

Casing.ToSnake("ParseLowerRun");
// → "parse_lower_run"

Casing.SnakeToCamel("parse_lower_run");
// → "parseLowerRun"

Casing.ToSnake("parseLowerRun");
// → "parse_lower_run"

Casing.CallableFromSnake("lower_run", "Parse");
// → "ParseLowerRun"
```

## Common patterns

**Generating function names from schema field names:**

```beskid
string fieldName = "user_id";
string getter = Casing.CallableFromSnake(fieldName, "Get");
// getter == "GetUserId"
```

**Validating identifier parts:**

```beskid
bool validStart = Ascii.IsIdentifierByte(byte, true);
bool validBody = Ascii.IsIdentifierByte(byte, false);
```

## Gotchas

- ASCII-only. Bytes above 127 are dropped, because each output character goes through `String.CodeUnitChar`, which has no one-byte form for them.
- Consecutive underscores in `SnakeToPascal` cause consecutive uppercase flips (each `_` sets `upperNext = true`), which may produce unexpected results for `__double_underscore` input.
