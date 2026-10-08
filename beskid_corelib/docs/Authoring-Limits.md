# Writing Corelib within the compiler's limits

Corelib code must compile and run on the released toolchain, 0.5.3 or later; 0.5.2 is no longer supported. These are the compiler and runtime gaps found while writing the string, number, collection, JSON, path, calendar, and testing modules, with the workaround each module uses. Each gap was first reproduced with `beskid 0.5.2`, the 0.5.3 compiler closes none of them, and each has a runnable canary listed in the [compiler fix list](./Compiler-Fix-List.md). The networking packages keep their own gap log with repros in `docs/networking/` (`COMPILER-GAPS.md`, `GAP-EVIDENCE.md`, `repros/`). "ICE" means an internal compiler error during lowering.

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
| Fully qualified generic calls | `Core.Collections.Queue.New<i64>()` ICEs. | `use Core.Collections.Queue;` and call `Queue.New<i64>()`. |
| Calls inside array literals | `[U(1), U(2)]` ICEs. | Build the array with `Array.Append`. |
| `bulk` parameters with several arguments | `List.Of<i64>(1, 2)` reports an arity error; passing one array ICEs. | `List.FromArray`, `Set.FromArray`, or array literals. |
| Array literals of enum values | ICE. | Build with `Array.Append`. |
| `f64` to `i64` cast | `i64(x)` on an f64 ICEs. | `Number.TruncateToI64`, a bit-by-bit decomposition. |
| Interpolating `f64` or `bool` | f64 ICEs; bool produces wrong text. | `Number.FormatGeneral`, `StringBuilder.AppendBool`. |

## Silent miscompiles

- **A method parameter named like a field of `this` reads the field.** In `pub string Echo(string text)` on a type with a `text` field, `text` is `this.text`, with no diagnostic. Never give a method parameter the name of one of the type's fields. (`StringBuilder` hit this: `Append(string text)` appended the empty `text` field.)

## Semantics to keep in mind

- **Integer literals default to `i32`.** `-9223372036854775807 - 1` evaluates as `i32`, and match arms mixing `0` with an `i64` call fail to lower (`InvalidMatchArms`). Suffix large or arm-result literals with `_i64`.
- **`==` on user structs compares identity**, not fields. Primitives and strings compare by value.
- **Strings have no ordering operators and `char` has no `==`.** Use `String.Compare`, `String.Less`, and byte values.
- **No `^` operator** and `>>` is arithmetic. Use `Hash.Xor` and `Hash.ShiftRightLogical`.
- **Float literals have no exponent form** (`1e308` does not parse). Write the digits out or compute them.
- **String literals only escape `\"`, `\\`, and `\${`.** Use `String.Newline()`, `String.Tab()`, `String.FromAscii(code)`.
- **Blocks cannot end in a value expression.** Use explicit `return` inside match-arm blocks.
- **Reserved words cannot be identifiers.** Besides the familiar ones, the grammar reserves `host`, `registry`, `scope`, `startup`, `init`, `dispose`, `with`, `launch`, `inject`, `single`, `transient`, `global`, `event`, `when`, `using`, `bulk`, `test`, `skip`, `spawn`, `clif`, `async`, `await`, `try`, and `catch`, so a field or local named `host` or `when` is a parse error. Since 0.5.3, identifiers that only start with a keyword (`hostName`, `spawnIt`, `in_range`) are accepted.
- **Types are imported through their module.** From another package, `use Console.Capabilities.ColorModel;` fails; import `Console.Capabilities` and write `Capabilities.ColorModel`.
- **Arrays are mutable reference values.** Element writes and `Array.Append` are visible through every alias: since 0.5.3, `Append` grows capacity geometrically and stores in place while capacity remains. A persistent value must never write to storage it may share. Append through `Core.Collections.Storage.AppendAt`, and build every other change into fresh storage with `Storage.CopyRange`, `CopyWithout`, `Concat`, or `Reversed`. `HashTable`, `StringMap`, `I64Map`, and `PriorityQueue` are single-owner values instead and update in place.
- **Text building.** On 0.5.2, appending 100 KB to a `u8[]` one byte at a time took about 20 s and exhausted the 1 GiB heap at 500 KB, because every append copied. `StringBuilder`, `Join`, `Replace`, and `Repeat` therefore concatenate through `String.Concat`. With 0.5.3's amortized `Append` and sized `Array.Zeroed`, re-measure a byte buffer before keeping that choice.
- **Arithmetic wraps** on overflow (no trap), which the hash functions rely on.

## Runtime defects

- **Interpolating the minimum `i64`** (`"${value}"` with `value == -2^63`) produces `-` alone. Use `Number.FormatI64`; `StringBuilder.AppendI64` and `Testing.Expect` already do.
- **Empty-plus-empty string concatenation** produces an invalid string that later fails to write. `String.Concat` avoids it; use it wherever both operands can be empty.
- **`Core.Time.ToUtcDateTime` does not compile when called.** Its body assigns to the non-`mut` locals `nanos` and `remaining`, which only surfaces once a caller pulls it into analysis. `Time.bd` is a compiler-embedded service file, so the fix must land in the compiler's copy too; `Core.Time.Calendar.ToDateTime` is the working replacement.
- **A failed assertion traps the whole test process**, so later tests in the target do not run. Keep expected-failure checks out of the suite.

## Testing a modified Corelib with a released binary

The compiler grants intrinsic access per service file: a Corelib file that the compiler also embeds (for example `Core/String/Core.bd`, `Core/Path/Path.bd`, `Core/Time/Time.bd`, `Core/Collections/Array.bd`, `Core/Bytes/Slice.bd`, and `Testing/Assert.bd`; the list is `beskid_abi/src/runtime_source/sources.rs` in the compiler) keeps its authority only while it sits at its canonical path and is byte-identical to the embedded copy. Other files, extra packages, and the `.beskid-bundle.sha256` marker do not affect it. New behavior therefore goes into new files, never into those service files; changing one needs a compiler rebuild from the same Corelib commit. To test, copy the working tree without `.git` and run `beskid test --project beskid_corelib/tests/corelib_tests --target <name>` from the copy, one target at a time; the copy no longer needs a recomputed marker. Never point `BESKID_CORELIB_ROOT` at a git checkout: the bundle hash is still an install integrity check, and a marked directory whose fingerprint differs is re-materialized from the embedded bundle. Runtime kits built for 0.5.2 do not work with 0.5.3 (trap code 11); rebuild them with `beskid runtime-kit build-native-host`.
