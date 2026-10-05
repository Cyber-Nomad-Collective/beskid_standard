# Compiler gaps found with beskid 0.5.2

Append: date, slice, symptom, minimal repro, workaround.

## 2026-10-05, codec: multi-line `///` doc comments inside a type body

Symptom: two consecutive `///` lines before a method inside `type X { ... }`
fail ("callable `value` should use PascalCase" or a parse error "expected
ImplMethodDefinition"): the second line is parsed as code.

Repro:
```
pub type A { i64 x,
    /// one line.
    /// two line.
    pub i64 F() { return this.x; }
}
```
Workaround: use `//` comments (or a single `///` line) inside type bodies.
Top-level multi-line `///` is fine.

## 2026-10-05, codec: floating `///` block before an item doc empties the module

Symptom: a file that starts with a `///` block, a blank line, and then a
documented item (`/// doc` + `pub ...`) compiles, but every item of the module
is reported as `unknown value X in module M` at use sites. No diagnostic in the
module itself.

Repro (`src/Codec/Be.bd`, module `pub mod Codec.Be;`):
```
/// Floating description line 1.
/// line 2.

/// Reads one.
pub i64 ReadOne() { return 1_i64; }
```
Workaround: use `//` for file-level comments, or attach the text to the first item.

## 2026-10-05, codec: sibling method call inside a type method is not lowered

Symptom: `internal compiler error: no ISLE lowering rule or fact for CallExpression`
(runtime test failure, not a compile diagnostic) for `this.Other(...)` inside a method.

Repro:
```
pub type C { i64 n,
    pub i64 A() { return this.n; }
    pub i64 B() { return this.A(); }
}
```
Workaround: put bodies in module-level functions `DoA(C self)` and make methods thin
wrappers `pub i64 A() { return DoA(this); }`. Calls to module functions with `this` work.

## 2026-10-05, codec: field assignment using a pattern-bound struct field

Symptom: ICE `no ISLE lowering rule or fact for AssignExpression` for
`Result::Ok(v) => { self.pos = self.pos + v.length; ... }` where `v` is a struct
(`Varint { value, length }`) bound by the match arm. The same assignment with a
local `i64` instead of `v.length` lowers fine.
Workaround: read the field into a local, or use a value already in scope.
