# Evidence for the compiler and runtime gap reports

Answers for the agent that fixes the gaps logged by the networking program.
All paths are local; nothing is pushed.

## 1. Authoritative sources

| What | Repository | Branch @ commit | Path |
| --- | --- | --- | --- |
| Integrated protocol stack (uri, codec, connect, crypto (pure), x509, tls, http2 HPACK, websocket + wss, quic, http3 + QPACK) | corelib (`compiler/corelib`, `beskid_standard`) | `claude/net-protocols` @ `bde3c41` | worktree `.worktrees/corelib-net-protocols/protocols/` |
| Main gap report | same | same | `protocols/COMPILER-GAPS.md` (C*, W*, X*, H*, Q*, tls/codec/uri sections) |
| Runnable repros (8 cases, outputs on both toolchains) | same | same (merged from `claude/net-repros` @ `68a726d`) | `protocols/repros/` (README.md per-case table) |
| Rulings | same | same | `protocols/RULINGS.md` |
| CLIF-optimized crypto + 0.5.3 gaps C53-1..6 + benchmarks | corelib | `claude/net-crypto-opt` @ `3c8dc4b` (not merged: needs 0.5.3) | `.worktrees/net-crypto-opt/protocols/{COMPILER-GAPS.md,crypto/BENCHMARKS.md}` |
| HTTP/2 connection layer + its gaps | corelib | `claude/net-h2` (in progress, last `51922a7`) | `.worktrees/net-h2/protocols/` |
| HTTP/3 over real QUIC | corelib | `claude/net-h3quic` (in progress) | `.worktrees/net-h3quic/protocols/` |
| Compiler 0.5.3 | compiler | `claude/v0.5.3` @ `ddbd6c3d` (+ uncommitted performance work in progress) | `.worktrees/compiler-v0.5.3` |

Gaps not yet in the merged report: HTTP/2 connection-layer entries (on `claude/net-h2`) and
C53-1..6 (on `claude/net-crypto-opt`). There are no other unrecorded gaps.

Fixed already (skip): keyword-prefixed identifiers (C8, H1, `host_*`, `spawnIt`, `neverName`,
`clif_xor`, `in_range`) — compiler `ddbd6c3d` on `claude/v0.5.3`; whole-tree corelib bundle
authority — `88522d60`.

## 2. Toolchains that produced the feedback

| Use | Binary | Version | Kit | Platform |
| --- | --- | --- | --- | --- |
| All protocol slices (uri ... http3, wss) | `/opt/homebrew/Cellar/beskid/0.5.2/libexec/bin/beskid` | `beskid 0.5.2` (release `cli-v0.5.2`, compiler `95c203ff`) | `/Users/mikserek/Projects/beskid/.worktrees/net-kit-0.5.2` (built by `beskid runtime-kit build-native-host --prefix <kit> --profile release` with the same CLI, because the Homebrew kit fails its hash check, see section 6) | macOS 26 (Darwin 25.5) arm64 |
| Crypto optimization, repro recheck | `/target/compiler-v053/release/beskid_cli` (container `beskid-codex-build` on 10.66.0.2) | `beskid 0.5.3` (branch `claude/v0.5.3` @ `09b6104e`, binary mtime 2026-10-05 13:26:57 UTC) | `/workspace/v053-kit` | Linux 6.6.94 x86_64 (Ryzen 7 7700) |

Command shape (both): `BESKID_RUNTIME_PREFIX=<kit> beskid test --project protocols/<pkg>/tests [--target <T> | --all-targets] --plain --target-timeout <s>` with `BESKID_CORELIB_ROOT` unset. Packages depend on an unmodified 0.5.2 corelib copy at `.worktrees/corelib-0.5.2-pristine` (builder: `/workspace/corelib-0.5.2-pristine`).

Rechecked with 0.5.3: the 8 repro cases (identical results to 0.5.2, outputs in
`protocols/repros/<case>/actual-0.5.3-linux.txt`) and the whole crypto suite (21/21 green, where
C53-1..6 were found). The other gap entries were observed on 0.5.2 only.

## 3. Complete repros

`protocols/repros/<case>/` each with `<case>.bproj`, `src/Main.bd` (+ variant files), `run.sh`
(one `beskid test --target` per variant; set `BESKID_RUNTIME_PREFIX`, optional `BESKID=<cli>`),
`actual-0.5.2-macos.txt`, `actual-0.5.3-linux.txt`.

| Case | Actual error (both toolchains) | Correction to COMPILER-GAPS |
| --- | --- | --- |
| `module_variant` (`Module.Variant(x)`) | ``unknown value `Square` in module `Repro::Shapes` `` (semantic analysis) | not an ICE in a minimal layout; the TLS-slice ICE needed the larger context |
| `try_contract_arg` (`?` on a call with a contract argument) | `try operator requires a Result value with an Ok payload` (type check) | not the `TryExpression` ICE in a minimal layout |
| `contract_field` | `internal compiler error: semantic fact `abi_type` is unavailable` | confirmed; also `return match IO.Read(reader, ...)` → `no ISLE lowering rule or fact for MatchExpression` |
| `this_other` | `internal compiler error: no ISLE lowering rule or fact for `CallExpression`` | confirmed |
| `fiber_string_join` (`Fiber<string>.Join()`) | same `CallExpression` ICE | confirmed (`Fiber<i64>` works) |

## 4. Performance acceptance (compile time)

Codegen per test dominates. Reproduce on the Mac toolchain above (times measured on a loaded
host, load 8–15):

| Package | Target(s) | Observed | Command |
| --- | --- | --- | --- |
| x509 | `ChainRsa`, `ChainEc` (1 test each) | 103 s, 94 s; parsing 30–50 s per test | `beskid test --project protocols/x509/tests --target ChainRsa --plain --target-timeout 600` |
| tls | `Rfc8448Client`, `Engine`, `LoopbackPolicy`, `Loopback` (1 test each) | 170 s, 204 s, 256 s, 275 s; whole matrix 27.5 min; 544 reachable functions → 2m15s, 722 → 4m10–4m35 CLIF generation | `--project protocols/tls/tests --target Loopback --target-timeout 900` |
| quic | `QuicConnection`, `QuicConnectionStress`, `QuicLoopback`, `QuicTlsLoopback` | 453 s, 517 s, 532 s, 509 s; matrix 53 min | `--project protocols/quic/tests --target QuicTlsLoopback --target-timeout 900` |
| http3 | `H3ExchangeTests` (3), `H3ProtocolErrorTests` (4), `H3PeerTests` (2) | 141 s, 156 s, 81 s (40–57 s per connection test) | `--project protocols/http3/tests --target H3ExchangeTests --target-timeout 900` |
| websocket (wss) | `WsTlsTests` (2) | 18 m 56 s (~9 min per TLS-reaching test) | `--project protocols/websocket/tests --target WsTlsTests --target-timeout 2400` |

Correctness after removing workarounds: every package's full matrix must stay green, run as
`beskid test --project protocols/<pkg>/tests --all-targets --plain --target-timeout 900 --matrix-timeout 7200`
for uri, codec, connect, crypto, x509, tls, http2, websocket, quic, http3 (pass counts are in each
slice's report; summary: uri 9/9, codec 8/8, connect 8/8, crypto 18/18 (21/21 on the optimized
branch), x509 9/9, tls 8/8, http2 HPACK 9/9, websocket 9/9 + WsTlsTests, quic 9/9, http3 8/8).
Interop scripts: `protocols/tls/tests/interop/run.sh` (OpenSSL 6/6), `protocols/websocket/tests/interop/run.sh` (Node 7/7).

## 5. Runtime regressions

Runnable cases: `protocols/repros/{channel_exhaustion,array_oom,cancelled_parent_orphan}`, run on
0.5.2 (macOS) and 0.5.3 (Linux; the 0.5.3 runtime kit is the newest runtime built from the 0.5.3
branch). Results identical on both:

- channel_exhaustion: `Receive` first fails at iteration 65 with plain create (A), with `Close`
  each iteration (B), and with `Close` + `Assert.CollectGarbage()` each iteration (C). Close and
  GC release nothing.
- array_oom: three live 64 KiB arrays trap `out_of_memory (5): R1 req=65536 live=213120 ...
  cap=1073741824`; one 192 KiB array traps `req=180224 live=180224`; dropping references and
  calling `CollectGarbage` between allocations still traps on the third (`req=65536 live=65600`).
- cancelled_parent_orphan: `Join` returns `Error(Cancelled)`; the parent's parked `Receive`
  returns `Error(Cancelled)` and code after the park DOES run (C11's "never runs" is wrong);
  the child is orphaned and sets its flag at ~550 ms.

## 6. Homebrew failure

- Install: `brew install cyber-nomad-collective/beskid_homebrew/beskid` (tap git head
  `4851ca1cb6f0bc76555a9bb2393576a488308064`, Homebrew 7.0.7, `poured_from_bottle: false`).
- Formula: version `0.5.2`, url
  `https://github.com/Cyber-Nomad-Collective/beskid_compiler/releases/download/v0.5.2/beskid-0.5.2-aarch64-apple-darwin.tar.gz`,
  sha256 `8982185362c8f8ad6799edbf5304af77c4545b3e2784e0945ead43877671f387`;
  `install` copies `bin lib beskid_corelib release-version.txt` into `libexec`.
- Failing file:
  `/opt/homebrew/Cellar/beskid/0.5.2/libexec/lib/beskid-runtime/abi-5/aarch64-apple-darwin/release/shared/libbeskid_runtime.dylib`
- Expected `19802e88dd6453682ce83a797ecd8b87c9d5b37d83df9506f6bf9066c62de187`, actual
  `b61fd40c8d388250f89eb0244bf87119b9b7110b382f4a1c5142b49b890ebcfa`.
- Complete error (any `beskid test`/`run`):
  `failed to initialize exact ABI-v5 runtime kit: ABI-v5 runtime kit validation failed: Resolution(ArtifactHashMismatch { path: "<file above>", expected: "19802e88…", actual: "b61fd40c…" })`
- Cause evidence: `otool -L` shows the dylib's install name rewritten to
  `/opt/homebrew/opt/beskid/libexec/lib/beskid-runtime/abi-5/aarch64-apple-darwin/release/shared/libbeskid_runtime.dylib`,
  and `codesign -dv` shows `Signature=adhoc` — Homebrew's install-time relocation and re-sign
  change the file bytes. Tracked by v0.6 as WEB-KIT01.
