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

## 2026-10-05, codec: contract value stored in a struct field, or forwarded with `this`

Symptom A: `internal compiler error: no ISLE lowering rule or fact for StructLiteralExpression`
when a struct literal initializes a field whose declared type is a contract
(`pub type Holder { Reader source, ... }` with `source: MemReader { ... }`); using
such a value later gives `semantic fact abi_type is unavailable`.
Workaround: pass the `Reader` as an argument to every operation.

Symptom B: `semantic fact call_abi_signature is unavailable` for a method that forwards
`this` plus a contract argument to a module function:
```
pub type G { i64 q,
  pub Result<i64, IoError> M(Reader r, u8[] b) { return DoM(this, r, b); }
}
Result<i64, IoError> DoM(G self, Reader r, u8[] b) { return IO.Read(r, b, 0_i64, 1_i64); }
```
Calling `DoM(h, r, b)` directly (not from a method) works, as does forwarding `this.q`
instead of `this`. Workaround: operations that take a contract are module functions
(`Buffered.ReadLine(reader, source, max)`), not methods.

## 2026-10-05, codec: integer narrowing does not truncate

`u8(0x100000041_i64)` and `u32(0x100000041_i64)` are not equal to 0x41 (no wraparound
on narrowing from i64). Workaround: mask with `& 255_i64` / `& 0xFFFFFFFF_i64` first.
