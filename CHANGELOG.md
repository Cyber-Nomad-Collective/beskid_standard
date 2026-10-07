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

- Build `StringBuilder` output by string concatenation instead of per-byte
  `u8[]` growth, which 0.5.2 performs far more slowly; keep `Join`, `Replace`,
  and `Repeat` on concatenation for the same reason.
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
