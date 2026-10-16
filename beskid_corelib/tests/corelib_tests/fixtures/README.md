# Corelib source fixtures

These fixtures are intentionally outside the ordinary all-targets unit-test matrix.

- `compile-fail/LegacyCollectionsNamespace.bd` must fail module resolution, proving the retired `Collections.*` namespace has no alias or re-export path.
- `compile-fail/parallel/` holds one target per `Core.Parallel` rejection (captured `Scope`, use after `Freeze`, non-Shared frozen capture, non-transferable port and sequence elements, missing `Commutative`, captured mutable local). Each entry declares its code on a `// EXPECT: <code>` line, like `compile-fail/legality/`.
- `native-only/ArrayAppendOverflow.bd` is executed only by the native bounded-allocation harness and must trap with `arithmetic_overflow`. It uses the public `Core.Collections.Array.Append` API and does not fabricate a local result.

Native-only fixtures require an installed ABI-v5 runtime kit and are not valid JIT substitutes.
