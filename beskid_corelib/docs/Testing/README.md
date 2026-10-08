**Testing** helpers for Beskid `test` blocks and user-authored tests.

## Modules

- [Testing.Assert](./Assert.md) — Shouldly-style assertions (`Equal`, `True`, `False`, `Contains`, `Fail`) with **actual-first** argument order.
- [Testing.Expect](./Expect.md) — typed expectations whose failure messages show expected and actual values.
- [Testing.Contracts](./Contracts.md) — Deferred predicate/message contracts for staged assertion tooling.

Deprecated `Testing.Assertions` (expected-first wrappers) has been removed; import `Testing.Assert` directly.
