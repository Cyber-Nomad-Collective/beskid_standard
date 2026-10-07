# Writing Corelib for the 0.5.2 compiler

Corelib code must compile and run on the released toolchain. These are the gaps in the 0.5.2 compiler and runtime found while writing the string, number, collection, JSON, path, calendar, and testing modules, with the workaround each module uses. Each gap was reproduced with the shipped `beskid 0.5.2` binary; "ICE" means an internal compiler error during lowering.

## Language features that do not lower

| Gap | Symptom | Workaround |
|-----|---------|------------|
| Lambdas and function values | Any lambda, lambda-typed parameter, or function-typed field fails in codegen (`abi_type unavailable`, `StructLiteralExpression`). Named functions cannot be passed as values. | No callbacks. Collections take parallel key arrays (`Sort.ByI64Key`) or caller-computed hashes (`HashTable`). |
| Contract dispatch on bounded generics | `where T: Contract` type-checks, but `a.Method()` on a `T` is rejected. | Specialize per key type (`StringMap`, `I64Map`) or rely on `==`. |
| Generic methods | Methods cannot declare their own type parameters; methods of a generic type cannot mention `T` in a function type. | Module-level generic functions. |
| Locals of a type-parameter type | `T value = ...;` inside generic code ICEs. | Inline the expression, or hold the value in a one-element `T[]` (see `PriorityQueue.SwapItems`). |
| Method calling a method on `this` | `this.Append(...)` inside a method ICEs. | Methods delegate to private module functions taking the receiver. |
| `match` yielding `self` or a generic value inside a method | ICE. | Move the logic into a module function that uses `if` and early `return`. |
| Nested field access through a struct field | `value.time.hour` and `this.table.count` ICE. | Copy the inner struct to a local first, or read through an accessor function. |
| Field access on a call result | `Calendar.AddDays(d, 1).day` ICEs. | Bind the result to a local first. |
| `bulk` parameters with several arguments | `List.Of<i64>(1, 2)` reports an arity error; passing one array ICEs. | `List.FromArray`, `Set.FromArray`, or array literals. |
| Array literals of enum values | ICE. | Build with `Array.Append`. |
| `f64` to `i64` cast | `i64(x)` on an f64 ICEs. | `Number.TruncateToI64`, a bit-by-bit decomposition. |
| Interpolating `f64` or `bool` | f64 ICEs; bool produces wrong text. | `Number.FormatGeneral`, `StringBuilder.AppendBool`. |
| Interpolation with two or more holes | Not lowerable. | Concatenate single-hole strings. |

## Semantics to keep in mind

- **Integer literals default to `i32`.** `-9223372036854775807 - 1` evaluates as `i32`, and match arms mixing `0` with an `i64` call fail to lower (`InvalidMatchArms`). Suffix large or arm-result literals with `_i64`.
- **`==` on user structs compares identity**, not fields. Primitives and strings compare by value.
- **Strings have no ordering operators and `char` has no `==`.** Use `String.Compare`, `String.Less`, and byte values.
- **No `^` operator** and `>>` is arithmetic. Use `Hash.Xor` and `Hash.ShiftRightLogical`.
- **Float literals have no exponent form** (`1e308` does not parse). Write the digits out or compute them.
- **String literals only escape `\"`, `\\`, and `\${`.** Use `String.Newline()`, `String.Tab()`, `String.FromAscii(code)`.
- **Blocks cannot end in a value expression.** Use explicit `return` inside match-arm blocks.
- **Arithmetic wraps** on overflow (no trap), which the hash functions rely on.

## Runtime defects

- **Interpolating the minimum `i64`** (`"${value}"` with `value == -2^63`) produces `-` alone. Use `Number.FormatI64`; `StringBuilder.AppendI64` and `Testing.Expect` already do.
- **Empty-plus-empty string concatenation** produces an invalid string that later fails to write. `String.Concat` avoids it; use it wherever both operands can be empty.
- **`Core.Time.ToUtcDateTime` does not compile when called.** Its body assigns to the non-`mut` locals `nanos` and `remaining`, which only surfaces once a caller pulls it into analysis. `Time.bd` is a compiler-embedded service file, so the fix must land in the compiler's copy too; `Core.Time.Calendar.ToDateTime` is the working replacement.
- **A failed assertion traps the whole test process**, so later tests in the target do not run. Keep expected-failure checks out of the suite.

## Testing a modified Corelib with a released binary

The compiler grants intrinsic access only to a Corelib bundle whose `.beskid-bundle.sha256` matches the SHA-256 of the whole tree, and only to service files byte-identical to the copies embedded in the compiler (for example `Core/String/Core.bd`, `Core/Path/Path.bd`, `Core/Time/Time.bd`, and `Testing/Assert.bd`). New behavior therefore goes into new files, never into those service files. To test, copy the working tree without `.git`, `obj`, and `Project.lock` files, write a recomputed marker, and run `beskid test` from the copy. Never point `BESKID_CORELIB_ROOT` at a git checkout: 0.5.2 treats a marked directory as a managed install and replaces it with the embedded bundle.
