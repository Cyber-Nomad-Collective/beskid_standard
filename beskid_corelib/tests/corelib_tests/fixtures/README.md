# Corelib source fixtures

These fixtures are intentionally outside the ordinary all-targets unit-test matrix.

- `compile-fail/LegacyCollectionsNamespace.bd` must fail module resolution, proving the retired `Collections.*` namespace has no alias or re-export path.
- `native-only/ArrayAppendOverflow.bd` is executed only by the native bounded-allocation harness and must trap with `arithmetic_overflow`. It uses the public `Core.Collections.Array.Append` API and does not fabricate a local result.

Native-only fixtures require an installed ABI-v5 runtime kit and are not valid JIT substitutes.
