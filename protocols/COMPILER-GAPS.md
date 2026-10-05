# Compiler gaps found with beskid 0.5.2

Append: date, slice, symptom, minimal repro, workaround.

## 2026-10-05, crypto (public-key half)

### Member access on a call result fails to lower
- Symptom: `internal compiler error: no ISLE lowering rule or fact for MemberExpression (MissingRuleOrFact)`.
- Repro: `i64 t = Time.MonotonicNow().nanos;`
- Workaround: bind the call result first: `Core.Time.Instant now = Time.MonotonicNow(); i64 t = now.nanos;`

### Fully qualified call without a `use` fails to lower
- Symptom: `internal compiler error: no ISLE lowering rule or fact for CallExpression (MissingRuleOrFact)`.
- Repro: `string Dec(i64 v) { return Core.String.DigitChar(v); }` with no `use Core.String;`.
- Workaround: `use Core.String;` and call `String.DigitChar(v)`.

### Bare field names are not in scope inside `type` method bodies
- Symptom: `unknown value 'tag'`.
- Repro: `pub type Dummy: Hasher { i64 tag, pub u8[] Digest(u8[] data) { return [u8(tag)]; } }`
- Workaround: `this.tag`.

### Performance: `i64[]` element stores are about 10x slower than `u32[]` stores
- Symptom: a 256-iteration loop of `t[i & 15] = t[i & 15] + a[i & 15]` over `i64[]` takes ~3.7 us;
  the same loop over `u32[]` takes ~0.4 us. Loads are fast for both.
- Workaround: store limbs as `u32[]`, compute in `i64` locals (wrapping mul, logical `>>`).

### Performance: per-call cost of array arguments and array helpers
- Symptom (JIT, Apple silicon): each array argument of a call costs ~40 ns (an empty
  `unit F(u32[] a)` call ~42 ns, two arrays ~83 ns, no arrays ~1 ns); `Array.Len<T>(a)` ~65 ns;
  `Array.Append` ~200 ns per element, so `Slice.New(n)` costs ~200 ns per byte.
- Workaround: keep hot field arithmetic on one workspace array addressed by offsets
  (`Crypto.ModArith` W functions); allocate zeroed buffers from array literals trimmed with
  `Array.RemoveLast` (`BigNat.Zeros`, `BigNat.ZeroBytes`); pass lengths instead of calling `Array.Len`.

### Test-target compile time: every test recompiles its reachable code; 120 s target budget
- Symptom: `beskid test` runs "Generate CLIF" per test, for every function the test reaches,
  with no reuse across tests of one target. With ~90 reachable functions this was ~20 s per
  test, so a 7-test target hit `120-second target budget expired ... execute_tests`.
- Contributors measured: a `match` on `Result<Mont, PkError>` where `Mont` is a struct with
  five array fields costs ~0.8 s to compile; a 700-element `u8` literal written as `u8(0)`
  costs ~3 s while `0_u8` costs ~0.1 s; a 2048-element `u32` literal ~0.4 s.
- Workaround: avoid structs with many array fields on hot API paths (one workspace array
  instead), use literal suffixes (`0_u8`) instead of conversion calls in large literals,
  and keep test targets to a few tests each.

### Long straight-line function body fails to lower
- Symptom: `internal compiler error: no ISLE lowering rule or fact for Block (MissingRuleOrFact)`
  on a generated, fully unrolled 8-limb Montgomery multiply (~230 statements, ~45 `i64`
  locals, no loops) taking `(u32[] w, i64 out, i64 a, i64 b)`. Codegen time per test also rose by ~5 s.
- Workaround: keep the looped `ModArith.WMul`; the unrolled variant was dropped.
