# Changelog

All notable changes to the beskid core library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

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
