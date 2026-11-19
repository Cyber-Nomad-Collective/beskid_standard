`Testing.Assert` provides Shouldly-style assertion helpers for **`test`** blocks and harness-driven runs. Prefer **actual-first** argument order.

## Functions

| Function | Behavior |
|----------|----------|
| `Fail(string message)` | Unconditional failure via `__panic_str`. |
| `Equal<T>(actual, expected, because)` | Fails when values differ; the failure record holds the `Format()` text of both values. `T` must conform to `Core.Text.Formatting`. |
| `NotEqual<T>(actual, expected, because)` | Fails when values match unexpectedly; the record holds both values. `T` must conform to `Core.Text.Formatting`. |
| `True(condition, because)` / `False(condition, because)` | Boolean checks. |
| `Contains(text, needle, because)` | Uses `Core.String.Contains`; fails when no match. |

Pass `""` for `because` when no extra context is needed.

## Failure shape

Failures read like Shouldly diagnostics:

```
Assertion failed: should be 3 but was 5; because: array_new logical length mismatch
```

## Compatibility

`Testing.Assertions.*` remains as deprecated aliases (expected-first order) for one release cycle. New code should use `Testing.Assert.*`.
