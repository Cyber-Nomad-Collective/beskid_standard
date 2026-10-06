# Beskid compiler and runtime gap repros

Standalone projects that reproduce the gaps listed in `../COMPILER-GAPS.md`. Each case has a `<case>.bproj`,
`src/*.bd` with `test` blocks, a `run.sh`, and the captured output of two toolchains. A case has one target per variant:
`Gap` (or `A_`, `B_`, `C_` variants) shows the problem and `Workaround` shows the smallest working form.

Run a case: `BESKID_RUNTIME_PREFIX=<kit> ./<case>/run.sh` (set `BESKID=<path>` to pick a compiler; `run.sh` runs
`beskid test --project <case> --target <T> --plain | grep -v INFO` for every target). The corelib dependency is
`../../../../corelib-0.5.2-pristine/beskid_corelib`, so the case directories must sit four levels below the directory that
holds `corelib-0.5.2-pristine`.

## Toolchains

| | A: macOS | B: Linux |
|---|---|---|
| Compiler | Homebrew `beskid 0.5.2` (`/opt/homebrew/bin/beskid`) | `beskid 0.5.3` release build, `/target/compiler-v053/release/beskid_cli` (mtime 2026-10-05 13:26:57 UTC) |
| Platform | Darwin 25.5 arm64 | Linux 6.6.94 x86_64, NixOS builder container |
| Runtime kit | `/Users/mikserek/Projects/beskid/.worktrees/net-kit-0.5.2` | `/workspace/v053-kit` |
| Output file | `<case>/actual-0.5.2-macos.txt` | `<case>/actual-0.5.3-linux.txt` |

Output files keep the compiler progress lines (only `INFO` lines are removed). The result lines are near the end of each target block.

## Results

Every case gave the same result on both toolchains.

### module_variant
- Shows: an enum variant built through the module path, `Shapes.Square(4_i64)`, where `Shape` is declared in the module file `Repro/Shapes.bd`.
- Result (both): Gap fails at semantic analysis, not at CLIF time: `unknown value `Square` in module `Repro::Shapes`` (Main.bd:8:15, help: `check that module `Repro::Shapes` exports a value named `Square``). The ICE (`CallExpression`) named in COMPILER-GAPS did not reproduce in this layout; in the TLS slice the variant name type-checked. Workaround passes.
- Workaround: `Shape::Square(4_i64)`.

### try_contract_arg
- Shows: `i64 n = WriteVia(w, buf)?;` where `w` is a `Core.IO.Writer` parameter.
- Result (both): Gap fails at type check: `try operator requires a Result value with an Ok payload` (Main.bd:19:21, `invalid try target`; help: `apply `?` only to a `Result<Ok, Error>` expression`). `?` on the same call shape with no contract argument passes. COMPILER-GAPS reports a `TryExpression` ICE; on these toolchains the error is a type-check error with the same cause (contract argument in the call). Workaround passes.
- Workaround: bind the Result and `match` it.

### contract_field
- Shows: a struct with a field of contract type (`Reader source`) built from a `Core.IO.Reader` implementation and read through the field.
- Result (both): Gap fails: `internal compiler error: semantic fact `abi_type` is unavailable`. Workaround passes.
- Workaround: pass the reader as an argument to each operation. Side note found while writing the repro: `return match IO.Read(reader, ...) { ... };` with a contract argument gave `no ISLE lowering rule or fact for `MatchExpression``, so the helper uses a statement `match` with `return` in each arm.

### this_other
- Shows: method `B()` of a type returns `this.A()` (sibling method call).
- Result (both): Gap fails when the test runs: `internal compiler error: no ISLE lowering rule or fact for `CallExpression` (MissingRuleOrFact)`. Workaround passes.
- Workaround: bodies in module-level functions, methods call `DoA(this)`.

### fiber_string_join
- Shows: `Fiber<string> f = spawn (() => Name()); f.Join();`.
- Result (both): Gap fails: `internal compiler error: no ISLE lowering rule or fact for `CallExpression` (MissingRuleOrFact)`. Workaround passes.
- Workaround: `Fiber<i64>` (a code) or a `Fiber<Result<...>>`.

### channel_exhaustion
- Shows: create, send, receive (and optionally close, collect) up to 70 channels in a loop; prints the first iteration whose `Receive` fails.
- Result (both): all three variants fail at iteration 65 (the 65th `Channel.Create`): A plain, B with `Channel.Close` each iteration, C with `Close` plus `Testing.Assert.CollectGarbage()`. Variant A ends with the assertion trap `unreachable_or_isle_invariant (9): Assertion failed: should equal the expected value`; the printed line is `first failing Receive at iteration 65`. Close and GC do not release a slot.
- Workaround: create one channel and reuse it (70 rounds, no failure, passes).

### array_oom
- Shows: runtime heap limit for live `u8[]` arrays built by `Slice.New`.
- Result (both), identical numbers on both platforms:
  - A, live 64 KiB arrays kept in a `Blob[]`: the 3rd allocation traps: `beskid runtime trap v5: out_of_memory (5): R1 req=65536 live=213120 committed=1073741824 cap=1073741824`.
  - B, one 196608-byte array: `out_of_memory (5): R1 req=180224 live=180224 committed=1073741824 cap=1073741824`.
  - C, drop the reference and call `CollectGarbage` between allocations (one live array at a time): the 3rd allocation traps: `out_of_memory (5): R1 req=65536 live=65600 ...`. GC does not reclaim the earlier arrays in this loop.
- Workaround: small arrays (four live 16 KiB arrays pass); reuse scratch buffers.

### cancelled_parent_orphan
- Shows: a parent fiber spawns a child (sleeps 300 ms, then sets a flag in a shared `i64[]` only if the sleep completed) and parks on `Channel.Receive`; the scenario cancels the parent after 50 ms. The parent never joins the child. The scenario runs inside a spawned fiber because timer waits fail at once in a bare test body (W7).
- Result (both): `Join` of the cancelled parent returns `Error(Cancelled)`; the parent's `Receive` returned `Error(Cancelled)` and the code after the park DID run (`parent code after the park ran=yes, Receive result code=3`); at about 550 ms the child's flag is set (`child done=yes`), so the child outlived its cancelled parent (orphaned). The test ends with `Assertion failed: should equal the expected value` (the assert that the child did not run). This differs from the COMPILER-GAPS C11 text ("the cancelled fiber never runs code after the park"); the orphaning part is confirmed. C11 describes a parent parked in a `TcpStream.Connect` attempt chain, which this repro does not use.
- Workaround: the owner of both fibers cancels the child itself (`child.Cancel()`); the flag stays unset and the test passes.
