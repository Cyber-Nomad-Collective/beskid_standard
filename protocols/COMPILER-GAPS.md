# Compiler gaps found with beskid 0.5.2

Append: date, slice, symptom, minimal repro, workaround.

## 2026-10-05 crypto (symmetric half)

### Extern contracts cannot pass or receive byte buffers

- Symptom: `[Extern]` contract parameters accept only primitive scalars
  (`i8 u8 i32 i64 f64`, `pointer`). `u8[]` is rejected ("array types must use
  CBuffer or CArrayView"), but `CBuffer` is a non-primitive type and is rejected
  too ("only primitive types are permitted"), and package code has no way to get
  a `pointer` to a Beskid array or to read memory behind a C pointer.
- Repro:
  ```
  [Extern(Abi:"C", Library:"libc")]
  contract C { i32 getentropy(u8[] buffer, i64 length); }   // rejected
  ```
- Workaround (`Crypto/Entropy.bd`): `malloc` a C scratch buffer, `getentropy`
  into it, then copy the bytes back with `fmemopen` + `fgetc` (the mode string
  "r" is written with `memset`). One extern call per byte; fine for keys/nonces.

### `u32` is not an extern scalar

- Symptom: `u32 arc4random();` fails with "extern return type not allowed ...
  C profile disallows the return type-shape" (permitted: I8, U8, I32, I64, F64).
- Workaround: declare `uint32_t`/`size_t` results as `i32`/`i64`.

### Extern C symbol names trip the naming lint

- Symptom: W1633 "callable `getentropy` should use PascalCase" for every libc
  method in a contract declared in the root project; there is no attribute to
  map a PascalCase Beskid name to a C symbol.
- Workaround: accept the warning (not fatal); not reported for the contract
  inside the dependency package.

### `Library` does not appear to scope symbol lookup

- Symptom: on macOS a contract with `Library:"libc.so.6"` resolves and calls
  the macOS libc (`arc4random`, `getentropy` return real values). The library
  name seems to be ignored or to fall back to the process namespace. Linux
  behaviour was not tested here.
- Workaround: none needed on macOS; `Entropy` keeps the corelib pattern (Linux
  contract first, Darwin contract retry).

### `return` inside a block match arm is not typed `never`

- Symptom: `T x = match r { Result::Ok(v) => v, Result::Error(_) => { Assert.Fail("x"); return; }, };`
  fails with "type mismatch: expected T, got unit".
- Workaround: put the rest of the body inside the `Ok` arm and use a statement match.

### Struct fields cannot be declared `mut`

- Symptom: `type Ctx { u32[] h, mut i64 n, }` is a parse error.
- Workaround: keep mutable state in array fields (`i64[] meta`), which are mutable
  through a plain parameter; hash, MAC, and GHASH states use this layout.

### No sized array allocation outside corelib

- Symptom: `__array_new<u8>(n)` is rejected in package code; `Slice.New(n)`
  appends `n` times. Hot loops avoid it by allocating scratch arrays once per
  key or state.
