# Merging this Corelib work with the 0.5.3 line

This branch (`claude/clever-planck-08gn1w`, PR #11 and its follow-ups) was written and tested against the released 0.5.2 compiler. Some of the same features already exist on the 0.5.3 line. This guide is for whoever reconciles the two: what this branch adds or changes, which files will conflict, what behavior each test pins, and how to pick one implementation per feature without leaving two.

## Ground rules

- **One implementation per feature.** When 0.5.3 already has a module that this branch also adds (for example a TOML or URL parser), keep exactly one and delete the other along with its exports, docs, and tests that only exercised it. Do not keep both behind different names.
- **Tests are the specification.** Each module below lists its test targets. Before deleting either implementation, run the surviving one against *both* test sets. A failure is either a real bug or a documented behavior difference that needs an explicit decision (see [Behavior decisions](#behavior-decisions)).
- **Compiler-embedded files.** The compiler embeds some Corelib files byte-for-byte from the submodule (`Core/Time/Time.bd`, `Core/String/Core.bd`, `Core/Path/Path.bd`, `Testing/Assert.bd`, the `Platform/*` and `Runtime/*` sources, and others listed in `beskid_abi/src/runtime_source/sources.rs`). This branch does not modify any of them. Change those files only together with a compiler rebuild from the same Corelib commit.

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
| Compiler gaps | A `tests/canaries/*`, `docs/0.5.3-Compiler-Fix-List.md`, `docs/patches/0.5.3-time-mut.patch` | runnable canaries | `canaries/run.sh` |

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

## After the 0.5.3 compiler lands

1. Apply `docs/patches/0.5.3-time-mut.patch` and rebuild the compiler from that Corelib commit (`Time.bd` is embedded).
2. Run `beskid_corelib/tests/canaries/run.sh <beskid>` and, for every canary that reports `FIXED`, remove the workaround named in `docs/0.5.3-Compiler-Fix-List.md` (for example `String.Concat` guards once `EmptyConcat` passes, `Number.FormatI64` routing once `MinI64Interpolation` passes, and the one-element `T[]` holders once `GenericLocal` passes).
3. When `LambdaCall` and `ContractDispatch` pass, add comparator overloads to `Sort`, predicate overloads to `Query.Operators`, and generic hashed maps, then retire the per-key-type `StringMap`/`I64Map` only after their tests pass against the generic replacement.
4. Update `docs/Authoring-Limits-0.5.2.md` (or retire it) once its gaps are closed.

## Validating a merge

The released-binary procedure used for this branch: copy the tree without `.git`, `obj`, and `Project.lock` files; write a recomputed `.beskid-bundle.sha256`; run `beskid test --project beskid_corelib/tests/corelib_tests --target <name>` for each target listed above. With a 0.5.3 compiler built from the merged Corelib commit, the bundle is trusted directly. Targets have a 120-second budget; split large test files (as the TOML tests are) rather than raising it.
