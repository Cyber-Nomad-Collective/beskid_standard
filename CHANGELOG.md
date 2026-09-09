# Changelog

All notable changes to the beskid core library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

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
- Mark the mutable floating-point random intermediate explicitly and strengthen bounded-random tests.
- Mark the recursively rendered Markdown fragment mutable before applying styles.
- Align Stack and Query tests with typed arrays and the current collection APIs.
- Remove a duplicate Syscall import that prevented the ergonomics target from resolving.
- Align Results and Optional tests with their leaf modules and generic construction APIs.
- Replace stale Time and concurrency test calls with current typed APIs.
- Type Random byte comparisons explicitly as `u8`.
