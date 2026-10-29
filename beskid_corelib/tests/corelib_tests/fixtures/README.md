# Corelib source fixtures

These fixtures are outside the ordinary all-targets unit-test matrix. Each directory under
`compile-fail/` is one project with one target per entry. Each entry declares the error code it must
produce on a `// EXPECT: <code>` line. The compiler gates in `crates/beskid_tests_projects/src/spine/`
compile every target and fail when a target compiles cleanly or reports a different code.

- `compile-fail/legality/`: one target per semantic legality code. Each entry calls a helper in
  `Helpers/` that holds exactly one violation, so the code is reported in a dependency unit.
- `compile-fail/parallel/`: one target per `Core.Parallel` rejection (captured `Scope`, use after a
  port send, non-Shared frozen capture, non-transferable port and sequence elements, missing
  `Commutative`, captured mutable local, moved seed, laundered contract value).
- `compile-fail/resolution/`: names that must not resolve. The retired `Collections.*` namespace has
  no alias or re-export, and ordinary programs cannot name the runtime composition lookup export.
