# Changelog

All notable changes to the beskid core library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Consolidate Stack, Set, and Query iteration on module-function APIs supported by typed lowering.
- Use module-function constructors for generic Result and Option values.
- Align Channel and Mutex wrappers with the canonical Optional/Results modules.

### Fixed

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
