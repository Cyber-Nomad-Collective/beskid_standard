# Changelog

All notable changes to the beskid core library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Add `Core.String.Search`, `Core.String.Transform`, and `Core.String.Builder`
  through the `Core.String` hub: ordinal `Compare`/`Less`, affix and
  occurrence search, `Split`/`Lines`/`Join`, `Replace`, `Repeat`, padding,
  ASCII case mapping, trimming, `Concat`, and a linear UTF-8 `StringBuilder`.
- Add `Core.Text.Number` with full-range `ParseI64`, `ParseHex`, `ParseF64`,
  typed `NumberError`, `FormatFixed`, `FormatGeneral`, `FormatHex`, and pure
  `TruncateToI64`/`RoundToI64` conversion.
- Add `Core.Collections.Sort` (stable merge sort, keyed sorting of any element
  type, binary search), `Hash`, a caller-hashed open-addressing `HashTable`,
  hashed `StringMap` and `I64Map`, an `i64`-priority `PriorityQueue`, and
  typed `CollectionError`.
- Extend `List` (`TryGet`, `First`, `Last`, `IndexOf`, `Contains`, `Set`,
  `Insert`, `RemoveAt`, `Remove`, `Reverse`, `Slice`, `Concat`, `ToArray`,
  `Clear`, `FromArray`), `Map` (`TryGet`, `GetOr`, `Keys`, `Values`,
  `Entries`, `Clear`), and `Set` (`Union`, `Intersect`, `Difference`,
  `IsSubsetOf`, `ToArray`, `FromArray`).
- Add `Core.Json`: RFC 8259 parsing with typed `JsonError` offsets, escape and
  surrogate-pair decoding, a nesting limit, compact and indented output, and
  value construction and access helpers.
- Add `Core.Path.Lexical` normalization, joining, relative paths, stems, and
  parents; `Core.Time.Calendar` constant-time date arithmetic, ISO weekdays,
  and RFC 3339 parsing and formatting; and `Testing.Expect` expectations that
  report expected and actual values.
- Add seeded property and model-based tests (sorting, hash maps against the
  linear `Map`, an all-collision hash table, the priority queue), a JSON
  accept/reject conformance corpus with random-tree round trips, UTF-8 and
  float edge cases, and a full 146097-day Gregorian-cycle calendar sweep
  checked against Python-generated reference dates.
- Add `Number.FormatI64`, correct for the minimum `i64` that 0.5.2
  interpolation prints as `-`; route `StringBuilder.AppendI64` and
  `Testing.Expect` messages through the same guard.
- Add `Ansi.Text` (escape stripping, display-width measurement with wide and
  zero-width code points, ANSI-aware truncation, padding, centering, and word
  wrap) and `Ansi.Modes` (synchronized output, bracketed paste, focus
  reporting, cursor shape, hyperlink ids, OSC 52 clipboard, OSC 9
  notifications).
- Add `Console.Controls.Table` (display-width columns, alignment, width caps
  with truncation, Unicode/ASCII/no borders), multi-line `Panel` bodies, and
  cluster-aware width (flags, ZWJ emoji, skin tones, VS16) in `Ansi.Text`;
  `Wrap` now re-opens active styles on continuation lines.
- Add `Capabilities.FromEnvironment` and `TerminalEnvironment` so color policy
  is a pure, testable function of `TERM`, `COLORTERM`, `NO_COLOR`,
  `FORCE_COLOR`, and TTY state; `ProbeStdout` now uses it.
- Add `Sgr.ForegroundArgsFor` and `BackgroundArgsFor` for an explicit color
  model, and a console reference page.
- Add runnable compiler-gap canaries (`beskid_corelib/tests/canaries`), a
  0.5.3 compiler fix list, and a `Time.bd` patch to apply with the compiler
  rebuild; record the silent method-parameter/field shadowing miscompile.
- Document the 0.5.2 compiler and runtime limits that shape these APIs, and
  how to test a modified Corelib with a released binary.

- Add the networking protocol packages to the corelib aggregate:
  `corelib_uri`, `corelib_codec`, `corelib_connect`, `corelib_crypto`,
  `corelib_x509`, `corelib_tls`, `corelib_http2`, `corelib_websocket`,
  `corelib_quic`, `corelib_http3`, and `corelib_web` (moved from `protocols/`
  to `packages/`, each with a README). Each package depends on Foundation and
  on the exact sibling packages it imports; tests depend on the aggregate.
  Requires compiler 0.5.3, which grants corelib authority per service file.
  Program notes, compiler gap log, rulings, and repros are in
  `docs/networking/`.
- Select an in-process OpenSSL 3 provider in `corelib_crypto` (ruling R27):
  `libcrypto.so.3` is an optional extern contract (compiler 0.5.3), so the
  aggregate still loads on hosts without OpenSSL 3. One-shot SHA-2, HMAC,
  AES-GCM and ChaCha20-Poly1305 use EVP when it is available and passes a
  known-answer self-test; otherwise, or with `BESKID_CRYPTO_PROVIDER=pure`,
  the CLIF kernels run. The opt-in `crypto-openssl` package is removed.
- Fix QUIC loss of datagrams on deadline-bounded receives (WEB7): the endpoint
  receives on a dedicated fiber without a deadline, and PTO probes carry
  in-flight flow-control credit frames.
- Cover duplicate HTTP `Host` rejection at the server transport boundary while
  the client withholds a declared request body.
- Cover deterministic same-direction UDP receive contention and concurrent
  opposite-direction send/receive with a channel rendezvous.
- Add `Core.Time.Sleep(Duration)` with four closed `TimerError` outcomes,
  checked monotonic deadlines, and one call-owned scheduler wait. Document
  fiber-only admission, sticky cancellation, and the unspecified clock epoch;
  cover the public result shape in the maintained Time frontend tests.
- Add checked byte-reader and byte-writer contracts and fixed-buffer cursors.
- Add `Core.IO` Reader, Writer, Closer, Stream and IoError contracts, transfer
  loops and explicit DisposeError cleanup conversion. Focused JIT, static AOT,
  and native-kit execution verifies reset-cause and orderly-EOF behavior.
- Add strict HTTP ASCII decoding with typed encoding failures.

- Publish the foundation `Core.Disposable` contract with typed `DisposeError`
  results for exactly-once scoped cleanup.

### Changed

- Unify helpers with the same behavior so each exists once. `Core.String.Ascii`
  holds the ASCII byte classes and hex digit values; `Number.DigitsAt` reads
  fixed-width digit fields; `Search.StartsWithAt` and `Search.SkipWhitespace`
  back the affix tests, JSON, and TOML; `Encoding.Utf8.AppendCodePoint` is the
  UTF-8 encoder; and `Core.Collections.Storage` (`CopyRange`, `CopyWithout`,
  `Concat`, `Reversed`, `IndexOf`) is the only copier for persistent
  collections, with one sized allocation per copy. Console controls use
  `String.Repeat`, `Core.Math`, and `Number.DigitsAt`.
- Remove the duplicates (breaking): `Casing.IsAsciiLower`, `IsAsciiUpper`,
  `IsAsciiDigit`, `IsSnakePartChar`, `PascalToSnake`, and `CamelToSnake` (use
  `Ascii.*` and `Casing.ToSnake`), `Pest.Expr.IsIdentChar`,
  `Encoding.Hex.HexToNibble`, `Encoding.Utf8.RuneByteLen` (use
  `String.Utf8RuneByteLen`), `Sort.Reverse` (use `Storage.Reversed`),
  `Console.Controls.Frame.Repeat` (use `String.Repeat`), the
  `Console.Format.Scan` forwarders, and the `Console.Format.Attributes` digit
  tables (`ParseHexNibble`, `ParseHexByte`, `ParseU8`, `ParseDecimalDigit`, and
  their result types).
- Build `StringBuilder` output by string concatenation instead of per-byte
  `u8[]` growth, which 0.5.2 performs far more slowly; keep `Join`, `Replace`,
  and `Repeat` on concatenation for the same reason.
- Replace the placeholder `Query.Operators.Map` (returned copies of a sample)
  and `Filter` (returned its second argument) with lambda-free `Where`
  (mask), `WhereEquals`, `WhereNotEquals`, `Distinct`, `CountOf`, `IndexOf`,
  `Concat`, `Reverse`, and typed `SumI64`/`SumF64`/`MinI64`/`MaxI64`/
  `AverageF64`; rename `FoldI64` to `SumI64`; sort `OrderBy` with the stable
  merge sort instead of bubble sort; rewrite the stale Query docs.
- Make the free-function forms of the `Ansi` cursor, erase, OSC, screen, and
  input-mode builders delegate to their methods instead of duplicating every
  sequence.
- Add `Core.Text.SemVer` (SemVer 2.0 parsing, precedence, bumps, and
  npm/Cargo-style requirements), `Core.Text.Glob` (plain and path-aware
  wildcards), `Core.Text.Csv` (RFC 4180), `Core.Text.Url` (RFC 3986 parsing,
  percent-encoding, query parameters, reference resolution), and
  `Core.Text.Toml` (TOML 1.0 into `TomlValue`), with reference pages and a
  guide for merging this branch with the 0.5.3 line.
- **Breaking:** `List.Get`, `Map.Get`, `Queue.Peek`, and `Stack.Peek` return
  `Result<_, CollectionError>` (`IndexOutOfRange(index, count)`,
  `KeyNotFound`, `Empty`) instead of `Result<_, string>`.
- Fix color downgrades: `RgbTo256Index` now picks the nearest xterm cube or
  gray-ramp entry (every gray previously mapped to black), and 16-color
  mapping picks the nearest palette entry including bright codes (white and
  black previously both mapped to red). Remove the faulty
  `ClampChannelBucket` and `DominantChannelIndex` helpers.
- Detect truecolor only for `COLORTERM=truecolor|24bit`, 256 colors only for
  `TERM` values containing `256color`, honor `FORCE_COLOR` levels, and treat
  an empty `NO_COLOR` as unset.
- Size `Console.Controls.Panel` by visible width so ANSI styling and wide
  characters no longer misalign its border; `Measure` no longer adds a row
  for a title drawn inside the top border, and over-wide lines truncate
  instead of pushing the border out.
- Correct the `Core.String` reference: `Contains` scans substrings, and the
  page now covers the full search, transform, and builder surface.
- Regenerate syntax SDK binding, node-kind, and traversal inventories for scoped `use`.
- Box every Channel payload through one descriptor-backed generic value shape.
  Document sender/queue/receiver ownership at commit, cancellation and close;
  retain committed values for FIFO drain and adapt Hub receive to the same slot.
- Document dynamically growing unbounded channel storage and add a close/drain
  exactly-once facade regression.
- Replace the scalar/static Fiber facade with move-only `Fiber<T>` instance
  Join, Detach, and idempotent parameterless Cancel methods. Preserve actual
  cancellation, stack-allocation, and panic metadata in `FiberError`; remove
  fabricated `FiberJoinStatus` payload conversion.
- Regenerate the compiler SDK from the current syntax authority, including the
  first-class `U32` primitive and the canonical CLIF/optional block-expression
  nodes used by reusable lowering.
- Bound `Core.Process` 0.4 to current-process identity, comparison, and
  termination; remove the fabricated `Run`/`ExitCode` child-process surface
  and `ProcessError` until an exact cross-platform ABI-v5 service exists.
- Represent generic text-parser success as one `TextParseSuccess<T>` product
  payload nested inside `TextParseResult<T>`, preserving the reusable public
  surface while matching the compiler's single-payload enum ABI.
- License the core library under Apache-2.0 and ship its license, notice, and
  scope guidance with compiler-embedded snapshots.

- Document the single per-package `.bpk` publication path and the superrepo's
  exact production-corelib plus first-party-template inventory.
- Hard-cut collections to `Core.Collections`, separate array logical length from capacity, and route insertion/removal through rooted append and descriptor-aware clearing operations.
- Purge the dead legacy `Collections` hub at `packages/foundation/src/Collections/` (no `Core.` prefix); `Core.Collections.*` is the sole collection hub. The `LegacyCollectionsNamespace` compile-fail fixture is retained as a regression guard.
- Align `Core.FS` with the canonical manifest intrinsic names and native public-API fixtures.
- Consolidate Stack, Set, and Query iteration on module-function APIs supported by typed lowering.
- Use module-function constructors for generic Result and Option values.
- Align Channel and Mutex wrappers with the canonical Optional/Results modules.

### Fixed

- Keep persistent `List`, `Stack`, `Queue`, `Set` and `Map` versions independent
  when two versions grow from one base. `Array.Append` grows storage in place
  with compiler 0.5.3, so `Core.Collections.Storage.AppendAt` appends in place
  only when the version owns the storage tip and copies the prefix otherwise.
- Keep earlier versions intact on removal and overwrite: `List.Pop`,
  `Stack.Pop`, and `Queue.Dequeue` no longer clear the shared slot, `Map.Remove`
  and `Set.Remove` copy instead of shifting shared storage, and `Map.Insert`
  copies before overwriting an existing key, all through the shared
  `Core.Collections.Storage` copiers. `HashTable`, `StringMap`,
  `I64Map`, and `PriorityQueue` document that they are single-owner values.
- Fix QUIC loopback datagram loss (WEB7): the `QuicEndpoint` receiver fiber now
  waits without a deadline, because a timed-out runtime receive can drop a datagram
  that was already read. A PTO probe also carries the in-flight credit frames
  (MAX_DATA, MAX_STREAM_DATA, MAX_STREAMS) again. The new `QuicCreditLoss` test
  checks this in memory with lost credit frames.
- `Crypto.Entropy` AOT link on macOS: compiler 0.5.3 links `libc.so.6` as
  `-lc`, so the libc link shim in the web interop script is removed (WEB4).
- Validate a request's `Host` field as soon as its header completes, before
  waiting for or interpreting the body framing.
- Reject HTTP header control and non-ASCII octets during parsing and serialization, including HTAB before OWS trimming.
- Remove the lossy public `AppendUtf8Rune` APIs from both `Core.String.Utf8`
  and the `Core.String` facade. Validated byte buffers now materialize only
  through the canonical RFC 3629-checked decoding path.
- Declare `ReadBytesWith` as `Result<u8[], SyscallError>` without a count-returning
  compatibility wrapper; retain the trusted raw syscall count ABI internally.
- Reject non-shortest UTF-8, surrogates, out-of-range scalar values and malformed
  Base64 padding/unused bits; preserve every valid UTF-8 byte during decoding.
- Validate whole source and destination ranges before byte-copy mutation or
  zero-length bypass, preserving overlap-safe unit-returning copy behavior.
- Replace unused legacy byte-error variants with the normative `InvalidRange`
  and `OutOfBounds` cases used by checked cursors.

- Route Core.Args tests through the public collection API and remove the unregistered duplicate Args test suite.
- Thread the active cursor through generated nested sequences, choices, repeats, and optional terms;
  preserve successful optional advances; stop regex class parsing before its closing delimiter; and
  keep grouped-alternation branch traversal bounded by its enclosing parenthesis. Generated literals
  now escape Beskid interpolation openers while preserving standalone `$`, quotes, and backslashes.
- Resolve console, parser, Pest, and regex helpers through explicit module imports so
  syntax-only lowering retains exact declaration edges instead of failing closed.
- Keep the corelib test workspace lock bound only to its checked-out workspace
  packages, avoiding duplicate installed-prefix package authorities.
- Point the OS-thread surface test at the canonical `Core.Threading.Thread`
  module and stop executing an invalid null native entry routine as a test.
- Align the compiler SDK gate with the canonical Collect facade's current
  `0.5.0` contract version.
- Preserve UTF-8, Hex, and Base64 error context in a shared nominal payload
  compatible with the single-payload enum ABI; route codec buffer operations
  through the explicit `Core.Bytes.Slice` boundary and use `u8` Base64 alphabet
  indices.
- Resolve string helpers through an explicit `Core.String` import in parser
  primitives so syntax-only call lowering retains an exact declaration edge.
- Mark Query operator accumulators, bounded counts, materialized arrays, and
  sort flags mutable where their implementations reassign them.
- Convert the manifest-defined word result of `__str_len` explicitly at the
  public `Core.String.Len` i64 boundary.
- Align threading and filesystem gates with the canonical module path and
  expression grammar.
- Route forced collection in runtime-sensitive tests through the unit-returning
  `Testing.Assert.CollectGarbage` helper while keeping raw GC service authority compiler-owned.
- Preserve pointer-bearing collection values across growth and forced GC, clear removed slots, maintain queue-head semantics, and preserve typed `Result` errors through mapping and FS propagation.
- Replace legacy `AppendAt` and capacity-as-length consumers; add namespace rejection and native overflow source fixtures.
- Make console panel/progress rendering and ASCII casing conversions explicit across `i32`,
  `i64`, and `u8` boundaries, and cover exact progress-bar fill and clamping behavior.

- Prevent the Sgr module import from shadowing StyleChain builder functions.
- Assert monotonic clock ordering without requiring its arbitrary epoch to be positive.
- Delegate deprecated console whitespace trimming to the canonical Core.String implementation.
- Normalize signed random remainders into documented non-negative integer ranges.
- Convert the mutable random integer explicitly before floating-point
  normalization, allocate byte-test buffers through `Core.Bytes.Slice`, and
  assert exact deterministic seeded boolean and byte results.
- Mark the recursively rendered Markdown fragment mutable before applying styles.
- Align Stack and Query tests with typed arrays and the current collection APIs.
- Remove a duplicate Syscall import that prevented the ergonomics target from resolving.
- Align Results and Optional tests with their leaf modules and generic construction APIs.
- Replace stale Time and concurrency test calls with current typed APIs.
- Type Random byte comparisons explicitly as `u8`.

