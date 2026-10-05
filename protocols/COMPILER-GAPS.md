# Compiler gaps found with beskid 0.5.2

Append: date, slice, symptom, minimal repro, workaround.

## 2026-10-05, http2 (HPACK slice)

1. **Detached `///` doc comment is a parse error, silent in dependencies.**
   Symptom: a `///` block followed by a blank line (file header comment) fails
   `beskid parse` with "expected Visibility, ModuleDeclaration, ...". When the
   file belongs to a path dependency, `beskid test` reports no parse error;
   every item of that module is just missing ("unknown value `X` in module",
   "unknown import path"). Repro: a library file starting with
   `/// About this file.` + blank line + `pub i64 F() { return 1_i64; }`, used
   from a test project. Workaround: use `//` for detached comments; run
   `beskid parse` on library files when a module looks empty.
2. **Literal argument for a `mut` array parameter is an ICE.**
   `u8[] E(mut u8[] out) { ... }` called as `E([])` fails at CLIF time with
   "no ISLE lowering rule or fact for `CallExpression`". Workaround: bind to
   `mut u8[] buf = [];` and pass `buf`.
3. **Field access on a call result is an ICE.**
   `F(x).field` and `Array.Get<T>(a, i).field` fail with "no ISLE lowering
   rule or fact for `CallExpression`". Seen also as a `BinaryExpression` ICE in
   `Slice.Len(src) - header.next` where `header` is a match-arm binding.
   Workaround: bind the call result (or the field) to a local first.
4. **`match` on a nested field path is an ICE.**
   `return match encoder.policy.huffman { ... };` fails with "no ISLE
   lowering rule or fact for `MatchExpression`". Workaround:
   `HuffmanMode mode = encoder.policy.huffman; return match mode { ... };`.
5. **`return` inside a block arm of `return match` types the arm as unit.**
   `return match r { Ok(d) => { Assert...; return d.value; }, ... };` is
   "type mismatch: expected i64, got unit". Workaround: use `match` as a
   statement with `return` in the arms and a trailing `return`.
6. **`return [];` in a function returning `u8[]` is "expected u8[], got unit".**
   Workaround: `return Slice.New(0_i64);`.
7. Tooling note: a failed `Assert.True/Equal` traps with a generic message
   ("should be true but was false"); the `because` text is not printed, and
   the remaining tests of the target do not run. Workaround: one property per
   test when diagnosing.
8. **Array literal with computed elements is an ICE.**
   `string[] p = ["a", "b" + n];` fails with "no ISLE lowering rule or fact
   for `ArrayLiteralExpression`" (all-literal arrays work). Workaround: start
   from the literal part and `Array.Append` the computed elements.
9. Tooling note: the default per-target budget is 120 s; on a loaded host a
   target of ~30 JIT-compiled tests can expire (`timed_out`). Raise it with
   `--target-timeout` / `BESKID_TARGET_TIMEOUT_SECS` or split targets.
