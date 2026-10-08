# Compiler fix list

Every gap below has a canary in `beskid_corelib/tests/canaries/`: a small test that asserts the correct behavior, so it fails while the gap is open and passes once it is fixed. Run them all with:

```sh
beskid_corelib/tests/canaries/run.sh /path/to/beskid
```

The runner prints `REPRODUCES` or `FIXED` per canary. Run it from an installed Corelib or a copy of the working tree (see [Writing Corelib within the compiler's limits](./Authoring-Limits.md)). All 19 reproduce on the released 0.5.2 binary and on the 0.5.3 compiler (built from compiler `45ac84fe`, Corelib `82ecd75`); the gaps target the v0.6 compiler.

## Ordered by Corelib impact

| Priority | Canary | Gap | Corelib workaround it would remove |
|----------|--------|-----|------------------------------------|
| 1 | `ParameterShadowsField` | A method parameter named like a field of `this` silently reads the field: wrong results, no diagnostic. | Field-name discipline in every method. |
| 1 | `LambdaCall` | Lambdas and function-typed parameters fail in codegen. | Comparator/predicate overloads for `Sort`, `Query.Filter`/`Map`, hash maps with custom hashers. |
| 1 | `ContractDispatch` | Contract methods cannot be called on a `where T: Contract` generic. | Per-key-type `StringMap`/`I64Map`; generic `Equatable`/`Hashable` collections. |
| 2 | `ThisMethodCall` | `this.Method()` inside a method ICEs. | Methods that cannot share logic with siblings (each `Ansi` builder method builds its own sequence; the free functions now delegate to the methods) and the module-function indirection in `StringBuilder`. |
| 2 | `GenericLocal` | Locals of a type-parameter type ICE. | One-element `T[]` holders (`PriorityQueue.SwapItems`), inlined expressions. |
| 2 | `MatchSelf` | `match` yielding `self` or a generic value in a method ICEs. | `HashTable.GetOr` and `List.RemoveFirstIn` indirections. |
| 2 | `NestedField` | `this.inner.count` through a generic field and `value.time.hour` through module types ICE. | `HashTable.Size`, local copies in `Calendar`. |
| 2 | `QualifiedGenericCall` | `Core.Collections.Queue.New<i64>()` ICEs. | Module imports for every generic call. |
| 2 | `FieldOnCall` | `Make().x` ICEs. | Temporary locals. |
| 3 | `BulkArgs` | `bulk` parameters reject several arguments; one array argument ICEs. | `List.FromArray`/`Set.FromArray` instead of the shipped `Of` constructors. |
| 3 | `EnumArrayLiteral`, `CallInArrayLiteral` | Array literals of enum values or concatenated calls ICE. | `Array.Append` chains. |
| 3 | `FloatToIntCast` | `i64(f64)` ICEs. | Bit-decomposition in `Number.TruncateToI64`. |
| 3 | `FloatInterpolation`, `BoolInterpolation` | f64 interpolation ICEs; bool interpolation prints the wrong text. | `Number.FormatGeneral`, `StringBuilder.AppendBool`. |
| 3 | `EmptyConcat` | Runtime: `"" + ""` yields an invalid string. | `String.Concat` everywhere two operands may be empty. |
| 3 | `MinI64Interpolation` | Runtime: interpolating `-2^63` prints `-`. | `Number.FormatI64`. |
| 4 | `StringOrdering` | Strings have no `<` (feature request). | `String.Compare`/`String.Less`. |

## Corelib fix that ships with the compiler build

`TimeToUtc`: `Core.Time.ToUtcDateTime` and its helpers assign to locals that are not declared `mut`, so any caller fails analysis. The fix is [`patches/time-mut.patch`](./patches/time-mut.patch) (only `mut` keywords). `Time.bd` is embedded into the compiler from the Corelib submodule, so apply the patch and rebuild the compiler from the same commit. Applied alone, the released compiler stops trusting `Time.bd` (service authority needs byte identity with the embedded copy) and every intrinsic-using Time caller fails. `Time.bd` is unchanged in 0.5.3, so the patch still applies.

```sh
git apply beskid_corelib/docs/patches/time-mut.patch
```

Verified on a patched copy with 0.5.2: the `TimeToUtc` canary passes, and `SystemTimeTests` and the network targets fail exactly as described.
