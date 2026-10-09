# Merging this Corelib work with the 0.5.3 line

This branch (`claude/clever-planck-08gn1w`, PR #11 and its follow-ups) was written and tested against the released 0.5.2 compiler. Some of the same features already exist on the 0.5.3 line. This guide is for whoever reconciles the two: what this branch adds or changes, which files will conflict, what behavior each test pins, and how to pick one implementation per feature without leaving two.

## Status and decisions

- **Targets.** This branch and PR #11 target `main` (the v0.6 line). 0.5.3 is a frozen patch release, so this branch's breaking changes (typed `CollectionError`, removed `Query.Operators.Map`/`Filter`/`FoldI64`) do not go into it. Branch `0.5.3` (`82ecd75`) is merged into this branch with `Storage.AppendAt` as the single append path for persistent collections; the v0.6 session merges 0.5.3 into `main`.
- **Toolchain.** 0.5.2 is no longer supported on this line. This branch is validated with a 0.5.3 CLI and runtime kits built from compiler `45ac84fe` (Corelib `82ecd75`): every `corelib_tests` target, one at a time, and every canary. The published 0.5.3 release replaces that local build once it is out, and `StringBuilder`, `Join`, and `Replace` still need a re-measure against a byte buffer.
- **Persistence.** `List`, `Stack`, `Queue`, `Set`, and `Map` are persistent: pops and dequeues leave shared storage alone, removals and overwrites copy through `Storage.CopyWithout` and `Storage.CopyRange`, and `CollectionsPersistenceTests` covers every branch shape. `HashTable`, `StringMap`, `I64Map`, and `PriorityQueue` are single-owner values.
- **Consolidation.** Each feature duplicated across the two lines (table under [Duplicated features to consolidate](#duplicated-features-to-consolidate)) gets one small PR into `main`, branched from this branch after 0.5.3 is merged there, and validated with the affected package targets.

## Ground rules

- **One implementation per feature.** When 0.5.3 already has a module that this branch also adds (for example a TOML or URL parser), keep exactly one and delete the other along with its exports, docs, and tests that only exercised it. Do not keep both behind different names.
- **Tests are the specification.** Each module below lists its test targets. Before deleting either implementation, run the surviving one against *both* test sets. A failure is either a real bug or a documented behavior difference that needs an explicit decision (see [Behavior decisions](#behavior-decisions)).
- **Compiler-embedded files.** The compiler embeds some Corelib files byte-for-byte from the submodule (`Core/Time/Time.bd`, `Core/String/Core.bd`, `Core/Path/Path.bd`, `Testing/Assert.bd`, the `Platform/*` and `Runtime/*` sources, and others listed in `beskid_abi/src/runtime_source/sources.rs`). This branch does not modify any of them. Change those files only together with a compiler rebuild from the same Corelib commit.

## Differential against the 0.5.3 line (superrepo `5703ca76`)

Superrepo `5703ca76` pins compiler `42d9f8cc` (tip of `0.5.3`, 28 commits after `v0.5.2`), which pins this repository at `91324fe` (tip of `0.5.3`). The common base with this branch is `7e3da7e`. The comparison below was first made statically; the merged branch has since been run on a local 0.5.3 build (see [Status and decisions](#status-and-decisions)).

### What a merge does

A trial `git merge origin/0.5.3` into this branch conflicts only in `CHANGELOG.md`, where both lines add entries under `[Unreleased]`; keep both lists. Everything else merges cleanly because the lines touch disjoint files. 0.5.3 adds eleven packages (`uri`, `codec`, `connect`, `crypto`, `x509`, `tls`, `http2`, `websocket`, `quic`, `http3`, `web`), registers them in `beskid_corelib/corelib.bproj`, adds `docs/networking/`, and changes two foundation files: `Core/Collections/Array.bd` and `Core/Bytes/Slice.bd`. This branch modifies neither file nor any other compiler-embedded file.

None of 0.5.3's packages uses `List`, `Map`, `Set`, `Queue`, `Stack`, `StringBuilder`, or `Query.Operators`, so this branch's breaking changes (typed `CollectionError`, `StringBuilder` field rename, removed `Map`/`Filter`/`FoldI64`) do not affect them. Every `Core.String` member they call still exists here.

### Compiler gaps: 0.5.3 fixes none of the 19 canaries

The 0.5.3 compiler commits cover optional externs, typed CLIF blocks, keyword-prefixed identifiers, geometric array growth, GC heap reuse, a network deadline race, and soname linking. None touches lambdas, contract dispatch, `this.Method()`, generic locals, `match` lowering, field access, array literals, casts, interpolation, or string concatenation, and `Time.bd` is unchanged at `91324fe`, so the `mut` patch still applies. 0.5.3's own gap log (`docs/networking/COMPILER-GAPS.md`, `packages/uri/COMPILER-GAPS.md`) independently reproduces `ThisMethodCall`, `FieldOnCall`, the array-literal ICEs, and `EmptyConcat` on the 0.5.3 compiler, and lists further gaps this branch did not hit (blocks as expressions, `mut` fields, conversion arguments, same-leaf imports, multi-line `///` comments). Every workaround in [Writing Corelib within the compiler's limits](./Authoring-Limits.md) therefore stays in place after the merge. Confirmed on a 0.5.3 build (compiler `45ac84fe`): all 19 canaries still reproduce. The gaps target the v0.6 compiler.

### Runtime changes that affect this branch

- **Array growth is geometric and in place.** On 0.5.3, `Array.Append` doubles capacity and, when capacity remains, stores in place, so every handle to the same array sees the new length. On 0.5.2 every append copied. This branch's collection code copies before mutating (`CopyPrefix`, fresh `Empty` plus `Append` in `Insert`, `Set`, `RemoveAt`, `Concat`, `Slice`, `ToArray`), so its values stay persistent. The pre-existing `List.Push`, `Queue`, `Stack`, and `Set` appended to the shared storage handle, so branching one version overwrote another; 0.5.3 fixed that with `Storage.AppendAt` (`82ecd75`), and this branch extends it to pops, removals, and overwrites (see [Status and decisions](#status-and-decisions)).
- **Byte buffers become cheap.** The 0.5.2 finding that `u8[]` growth is slower than string concatenation was caused by the copying append. Once 0.5.3 is the floor, re-measure `StringBuilder` and `Join`/`Replace`/`Repeat` with a `u8[]` buffer (or `Array.Zeroed`) and switch if faster.
- **Service authority is per file.** Compiler commit `88522d60` trusts a service source that sits at its canonical path and is byte-identical to the embedded copy; the bundle hash is only an install check. A Corelib copy with extra or changed non-service files keeps its intrinsics, so a copy of the tree no longer needs a recomputed marker.

### Duplicated features to consolidate

| Feature | 0.5.3 | This branch | Keep |
|---------|-------|-------------|------|
| URI parsing, formatting, resolution, dot segments, percent coding | `packages/uri` (`Uri.Parse`, `Format`, `Resolve`, `Normalize`, `Pct`; strict RFC 3986 with IPv4/IPv6/IPvFuture validation, normalization, 62 tests; used by `http3`, `websocket`, `web`) | `Core.Text.Url` (lenient, 4 tests, no callers) | **`packages/uri`.** Port `QueryParams` and `+`-as-space form decoding (with the `url_percent_coding_and_queries` cases) into it, then delete `Core/Text/Url.bd`, `docs/Core/Text/Url.md`, and the `url_*` tests. |
| Decimal formatting of `i64` | `Uri.Chars.DecimalText`, `Http2.Mapping.DecimalText`, `Http3.H3Mapping.DecimalText`, `X509.Der.Decimal` (wrong for negatives) | `Number.FormatI64` (full range) | `Number.FormatI64`. |
| ASCII case mapping | `Uri.Chars.LowerAscii`/`UpperAscii`, `X509.Certificate.Lower`, `Http.Codec.LowerAscii` | `String.ToLowerAscii`/`ToUpperAscii` | `Core.String`. |
| Prefix test, empty-safe concatenation | private `StartsWith` in `Mapping.bd`/`H3Mapping.bd`; `Uri.Chars.Cat`, `X509.Names.Join` | `String.StartsWith`, `String.Concat` | `Core.String`. |
| Civil-date arithmetic | `X509.Der.IsLeap`, `DaysInMonth`, `DaysFromCivil` | `Calendar.IsLeapYear`, `DaysInMonth`, `DaysFromCivil` (cycle-swept) | `Core.Time.Calendar`. |
| Hex text codec | `Codec.Hex.Encode`/`Decode` | existing `Core.Encoding.Hex` | `Core.Encoding.Hex`; `Codec.Hex` wraps it. |

No 0.5.3 package overlaps JSON, TOML, CSV, SemVer, Glob, hashing, sorting, priority queues, paths, `Testing.Expect`, or the console work. 0.5.3's streaming UTF-8 validator (`WebSocket.WsUtf8`) could later back `Core.Encoding.Utf8.IsValid`.

## Per-module inventory

Types are declared inside their module file, so from another package they are written `Module.Type` (for example `Toml.TomlValue`).

| Area | Files added (A) or changed (M) | Public surface | Test targets |
|------|--------------------------------|----------------|--------------|
| Strings | M `Core/String/Builder.bd`; earlier: A `Search.bd`, `Transform.bd`, `Builder.bd`, M `String.bd` hub | Search/transform functions on the `Core.String` hub; `StringBuilder` (field `content`) | `CoreStringOpsTests`, `CoreEdgeCaseTests` |
| Numbers | M `Core/Text/Number.bd` | `ParseI64`, `ParseHex`, `ParseF64`, `FormatI64`, `FormatFixed`, `FormatGeneral`, `FormatHex`, `TruncateToI64`, `RoundToI64`, `Pow10`, `IsFinite`, `NumberError` | `TextNumberTests`, `CoreEdgeCaseTests` |
| Collections | earlier: M `List.bd`, `Map.bd`, `Set.bd`, `Collections.bd`; A `Sort`, `Hash`, `HashTable`, `StringMap`, `I64Map`, `PriorityQueue`, `CollectionError` | see `docs/Collections` | `CollectionsExtendedTests`, `CollectionsPropertyTests` |
| JSON | earlier: A `Core/Json/*` | `Json.Parse`, `Stringify`, `Pretty`, `Quote`, builders, accessors, `JsonValue`, `JsonError` | `CoreJsonTests`, `CoreJsonConformanceTests` |
| Paths, time, testing | earlier: A `Core/Path/Lexical.bd`, `Core/Time/Calendar.bd`, `Testing/Expect.bd` | see `docs/Core` | `SystemPathLexicalTests`, `SystemCalendarTests`, `SystemCalendarSweepTests`, `TestingExpectTests` |
| Query | M `Query/Operators.bd` | `Where` (mask), `WhereEquals`, `WhereNotEquals`, `Distinct`, `CountOf`, `IndexOf`, `Concat`, `Reverse`, `SumI64`, `SumF64`, `MinI64`, `MaxI64`, `AverageF64`; `Map`, `Filter`, `FoldI64` removed | `QueryTests`, `QueryOperatorsExtendedTests` |
| SemVer | A `Core/Text/SemVer.bd` | `Parse`, `Format`, `Of`, `Compare`, `Satisfies`, bumps, `Version`, `SemVerError` | `TextFormatsTests` |
| Glob | A `Core/Text/Glob.bd` | `Match`, `MatchPath`, `HasWildcards` | `TextFormatsTests` |
| CSV | A `Core/Text/Csv.bd` | `Parse`, `ParseWith`, `Format`, `FormatWith`, `FormatField`, `Row`, `CsvRow`, `CsvError` | `TextFormatsTests` |
| URL | A `Core/Text/Url.bd` | `Parse`, `Format`, `PercentDecode`, `PercentEncode`, `QueryParams`, `Resolve`, `RemoveDotSegments`, `Url` (field `hostname`), `QueryParam`, `UrlError` | `TextFormatsTests` |
| TOML | A `Core/Text/Toml.bd` | `Parse`, accessors, `TomlValue`, `TomlError` | `TextTomlTests`, `TextTomlStringsTests`, `TextTomlStructureTests` |
| ANSI text | A `Ansi/Text.bd`, `Ansi/Modes.bd` | `Strip`, `VisibleWidth`, `ClusterAt`, `Truncate`, `Pad*`, `Center`, `Wrap`, `ActiveStyleAfter`; terminal modes | `ConsoleAnsiTextTests`, `ConsoleAnsiColorModesTests`, `ConsoleControlsTableTests` |
| Colors and capabilities | M `Ansi/Sgr.bd`, `Console/Capabilities.bd` | `ForegroundArgsFor`, `BackgroundArgsFor`, `NearestBasicIndex`, `CubeLevel`, `FromEnvironment`, `TerminalEnvironment`, `ProbeEnvironment` | `ConsoleAnsiColorModesTests` |
| Controls | A `Console/Controls/Table.bd`; M `Panel.bd` | `Table.*`; `Panel.BodyLines`, multi-line `Render`/`Measure` | `ConsoleControlsTableTests` |
| Builders | M `Ansi/Cursor.bd`, `Erase.bd`, `Osc.bd`, `Screen.bd`, `InputMode.bd` | unchanged API; free functions now delegate to methods | all `ConsoleAnsi*` targets |
| Compiler gaps | A `tests/canaries/*`, `docs/Compiler-Fix-List.md`, `docs/patches/time-mut.patch` | runnable canaries | `canaries/run.sh` |

## Expected conflict points

- **`corelib_tests.bproj`**: both lines append targets. Keep the union; target names on this branch are unique (`Text*`, `Console*`, `Collections*`, `Core*` prefixes). Remove the targets of whichever implementation you delete.
- **`CHANGELOG.md`**: keep both entry sets under `[Unreleased]`, then drop the lines for deleted implementations.
- **Hub files** (`Core/String/String.bd`, `Core/Collections/Collections.bd`, `Testing/Testing.bd`): union of `pub mod` lines and forwarders.
- **`Console/Capabilities.bd` and `Ansi/Sgr.bd`**: if 0.5.3 also reworked color detection, keep one policy. This branch's policy is a pure function of `TerminalEnvironment`, so it can be tested without touching the process environment; preserve that property in whichever version survives.
- **`Console/Controls/Panel.bd`**: `BodyLine` gained a `line` parameter and `Measure` changed its row count (see below).

## Behavior decisions

These are deliberate changes from 0.5.2 behavior; confirm or revert each explicitly while merging:

1. **Color detection**: plain `TERM=xterm` now selects 16 colors (was 256); only `COLORTERM=truecolor|24bit` selects truecolor (was any value); `FORCE_COLOR` levels 0-3 and empty `NO_COLOR` follow common conventions.
2. **Color downgrades**: nearest xterm palette entry replaces the previous mappings (grays mapped to black; white and black mapped to red).
3. **Query**: `Operators.Map` and `Filter` (placeholders) are removed and `FoldI64` is renamed `SumI64`. When 0.5.3 lambdas land, add real predicate/projection overloads rather than restoring the placeholders.
4. **Panel**: `Measure` no longer adds a row for the title (it is drawn in the top border) and returns one row per body line; over-wide lines truncate with `...`.
5. **`Url.hostname`**: named so because `host` is a reserved word.
6. **Typed collection errors (breaking)**: `List.Get`, `Map.Get`, `Queue.Peek`, and `Stack.Peek` return `Result<_, CollectionError>` instead of `Result<_, string>`. Callers that match `Result::Error(_)` are unaffected; callers that annotate `Result<T, string>` or read the message must switch to `CollectionError`. No caller in Corelib, the compiler repository, or `beskid_templates` depended on the strings at the time of this change.

## After the next compiler lands

1. Apply `docs/patches/time-mut.patch` and rebuild the compiler from that Corelib commit (`Time.bd` is embedded).
2. Run `beskid_corelib/tests/canaries/run.sh <beskid>` and, for every canary that reports `FIXED`, remove the workaround named in `docs/Compiler-Fix-List.md` (for example `String.Concat` guards once `EmptyConcat` passes, `Number.FormatI64` routing once `MinI64Interpolation` passes, and the one-element `T[]` holders once `GenericLocal` passes).
3. When `LambdaCall` and `ContractDispatch` pass, add comparator overloads to `Sort`, predicate overloads to `Query.Operators`, and generic hashed maps, then retire the per-key-type `StringMap`/`I64Map` only after their tests pass against the generic replacement.
4. Update `docs/Authoring-Limits.md` as its gaps close.

## Validating a merge

With the published 0.5.3 compiler, copy the tree without `.git` and run `beskid test --project beskid_corelib/tests/corelib_tests --target <name>` for each target listed above, one at a time; per-file service authority means the copy needs no recomputed marker. Runtime kits built for 0.5.2 must be rebuilt (`beskid runtime-kit build-native-host`). Targets have a 120-second budget; split large test files (as the TOML tests are) rather than raising it.
