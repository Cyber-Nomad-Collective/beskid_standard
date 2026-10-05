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

### No sized array allocation outside corelib; append growth is quadratic and capped

- Symptom: `__array_new<u8>(n)` is rejected in package code, so every buffer comes
  from `Slice.New(n)`, which appends `n` times. Measured on macOS arm64:
  32 x `Slice.New(16384)` takes ~5.5 s while 128 x `Slice.New(4096)` (same bytes)
  takes ~1.2 s, so the cost grows with the square of the size. A single array of
  ~180 KiB, or a few live 64 KiB arrays, traps with
  `out_of_memory (5): R1 req=180224 live=180224 committed=1073741824 cap=1073741824`.
- Repro: `test t { Assert.Equal<i64>(Slice.Len(Slice.New(200000_i64)), 200000_i64, "len"); }`
- Workaround: allocate scratch once per key/state, and use the in-place AEAD APIs
  (`ChaCha20Poly1305.SealInto/OpenInto`, `AesGcm.SealInto/OpenInto`) with a reused
  record buffer. With that, 16 KiB records seal and open at several MB/s under JIT.

## 2026-10-05, connect slice (Happy Eyeballs)

### C1. Spawn lambda capturing a match-bound value fails spawn legality
- Symptom: `spawn legality rejected ... StackReferenceEscapesSpawn` at ISLE emission.
- Repro:
  ```
  match listener.LocalAddress() {
      Result::Ok(addr) => { Fiber<unit> f = spawn (() => Use(addr)); f.Join(); },
      Result::Error(_) => (),
  };
  ```
- Workaround: copy into a local first (`SocketAddress target = addr;`) and capture the local.

### C2. `Fiber<string>.Join` has no lowering rule
- Symptom: `no ISLE lowering rule or fact for CallExpression` at `__fiber_join_value<T>` in `Concurrency/Fiber.bd`.
- Repro: `Fiber<string> f = spawn (() => Name()); f.Join();`
- Workaround: `Fiber<unit>`, `Fiber<i64>` and `Fiber<Result<TcpStream, NetworkError>>` / `Fiber<Result<SocketAddress[], NetworkError>>` lower fine; return a code or a Result instead of a string.

### C3. Spawn lambda with a compound body fails to lower
- Symptom: `no ISLE lowering rule or fact for CallExpression`.
- Repro: `spawn (() => Log("x: " + Try(target, 5_i64)))`
- Workaround: move the body into a named function and spawn `() => Body(a, b)` with plain arguments.

### C4. Fully qualified call without a `use` fails to lower
- Symptom: `no ISLE lowering rule or fact for CallExpression` (type check passes).
- Repro: `unit Log(string s) { Core.Output.WriteLine(s); return; }` with no `use Core.Output;`.
- Workaround: `use Core.Output;` and call `Output.WriteLine(s)`.

### C5. Nested match on a generic payload bound from a user enum variant
- Symptom: `no ISLE lowering rule or fact for MatchExpression`.
- Repro:
  ```
  pub enum Event { Outcome(i64 index, Result<TcpStream, NetworkError> result), Timer(i64 seq), }
  match ev {
      Event::Outcome(i, r) => { match r { Result::Ok(s) => { s.Close(); }, Result::Error(_) => (), }; },
      Event::Timer(_) => (),
  };
  ```
- Workaround: pass the payload to a helper function that does the inner match.

### C6. Match on a struct field of generic enum type
- Symptom: `no ISLE lowering rule or fact for MatchExpression`.
- Repro: `type P { pub Option<i64> max, }` then `return match p.max { Option::Some(v) => v, Option::None => 0_i64, };`
- Workaround: bind the field to a local first (`Option<i64> bound = p.max; match bound { ... }`), or use `Option.HasValue` / `Option.UnwrapOr`. Non-generic enum fields (`match address.address` on `IpAddress`) lower fine.

### C7. Array literal of struct locals
- Symptom: `no ISLE lowering rule or fact for ArrayLiteralExpression`.
- Repro: `SocketAddress a = ...; SocketAddress[] list = [a];`
- Workaround: `mut SocketAddress[] list = Array.Empty<SocketAddress>(); Array.Append<SocketAddress>(list, a);`. A literal of call expressions (`[A4(1_u8), A4(2_u8)]`) lowers fine.

### C8. Reserved and keyword-prefixed identifiers
- Symptom: parse error `expected Identifier or GenericArguments` for a parameter or local named `host` or `launch`; a local named `spawnIt` is lexed as `spawn It` (`unknown value It`).
- Repro: `pub i64 F(string host) { return 0_i64; }`, `mut bool launch = false;`, `bool spawnIt = true;`
- Workaround: rename (`hostName`, `kick`, `viaFiber`).

### C9. Imports bind the last path segment, so `X.Errors` collides with `Network.Errors`
- Symptom: `duplicate item name Errors` / `ambiguous import for Errors` when a test imports `Connect.Errors` and `Network.Errors`.
- Workaround: give package modules unique leaf names (`Connect.Failures`).

### C10. Runtime: channel table holds 64 channels per process; Close and GC never release
- Symptom: the 65th `Channel<T>.Create()` returns a handle whose `Receive` fails at once (status Closed/Cancelled), even after `Channel.Close` and `Testing.Assert.CollectGarbage()`.
- Repro:
  ```
  mut i64 i = 0_i64;
  while i < 200_i64 {
      Channel<i64> ch = Channel<i64>.Create();
      Channel<i64>.Send(ch, 1_i64);
      match Channel<i64>.Receive(ch) { Result::Ok(_) => (), Result::Error(_) => { Output.WriteLine("fails at 64"); return; }, };
      Channel<i64>.Close(ch);
      i = i + 1_i64;
  }
  ```
- Workaround: a library must not create a channel per call. Connect polls a preallocated `i64[]` completion-flag array written by child fibers and takes each child's typed result through `Fiber<Result<...>>.Join`.

### C11. Runtime: a cancelled fiber ends at its next park point without running code
- Symptom: after `fiber.Cancel()`, the target never observes `ChannelError::Cancelled` or `TimerError::Cancelled`; it stops inside `Receive`/`Sleep`, and `Join` reports `FiberError::Cancelled`. Its own child fibers are not cancelled and keep running unjoined.
- Repro: a parent spawns a child doing `TcpStream.Connect(..., 500 ms deadline)` that then sends on a channel, and parks on `Channel.Receive`; cancel the parent: the parent's code after `Receive` never runs, and the child's send still arrives 500 ms later.
- Workaround: none in library code. Connect documents that cancelling the calling fiber orphans in-flight attempt fibers: a failing attempt ends at the shared policy deadline, but an attempt that connects after the caller was cancelled leaves an unowned stream. Callers that cancel should set a policy timeout. Cancelling an attempt fiber that waits in `TcpStream.Connect` (what Connect does to losers) releases its pending socket; the exit leak audit reports nothing.

### C12. Blocks are not expressions
- Symptom: `type mismatch: expected string, got unit` for `Result::Ok(s) => { s.Close(); "ok" }`.
- Workaround: use `return` inside the arm, or a helper function.

## 2026-10-05, http2 (HPACK slice)

1. **Detached `///` doc comment is a parse error, silent in dependencies.**
   Symptom: a `///` block followed by a blank line (file header comment) fails
   `beskid parse` with "expected Visibility, ModuleDeclaration, ...". When the
   file belongs to a path dependency, `beskid test` reports no parse error;
   every item of that module is just missing ("unknown value `X` in module",
   "unknown import path"). Repro: a library file starting with
   `/// About this file.` + blank line + `pub i64 F() { return 1_i64; }`, used
   from a test project. Workaround: use `//` for detached comments; run
   `beskid parse` on library files when a module looks empty.
2. **Literal argument for a `mut` array parameter is an ICE.**
   `u8[] E(mut u8[] out) { ... }` called as `E([])` fails at CLIF time with
   "no ISLE lowering rule or fact for `CallExpression`". Workaround: bind to
   `mut u8[] buf = [];` and pass `buf`.
3. **Field access on a call result is an ICE.**
   `F(x).field` and `Array.Get<T>(a, i).field` fail with "no ISLE lowering
   rule or fact for `CallExpression`". Seen also as a `BinaryExpression` ICE in
   `Slice.Len(src) - header.next` where `header` is a match-arm binding.
   Workaround: bind the call result (or the field) to a local first.
4. **`match` on a nested field path is an ICE.**
   `return match encoder.policy.huffman { ... };` fails with "no ISLE
   lowering rule or fact for `MatchExpression`". Workaround:
   `HuffmanMode mode = encoder.policy.huffman; return match mode { ... };`.
5. **`return` inside a block arm of `return match` types the arm as unit.**
   `return match r { Ok(d) => { Assert...; return d.value; }, ... };` is
   "type mismatch: expected i64, got unit". Workaround: use `match` as a
   statement with `return` in the arms and a trailing `return`.
6. **`return [];` in a function returning `u8[]` is "expected u8[], got unit".**
   Workaround: `return Slice.New(0_i64);`.
7. Tooling note: a failed `Assert.True/Equal` traps with a generic message
   ("should be true but was false"); the `because` text is not printed, and
   the remaining tests of the target do not run. Workaround: one property per
   test when diagnosing.
8. **Array literal with computed elements is an ICE.**
   `string[] p = ["a", "b" + n];` fails with "no ISLE lowering rule or fact
   for `ArrayLiteralExpression`" (all-literal arrays work). Workaround: start
   from the literal part and `Array.Append` the computed elements.
9. Tooling note: the default per-target budget is 120 s; on a loaded host a
   target of ~30 JIT-compiled tests can expire (`timed_out`). Raise it with
   `--target-timeout` / `BESKID_TARGET_TIMEOUT_SECS` or split targets.

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

## 2026-10-05, tooling: per-test overhead and the 120 s target budget

Each `test` costs 1 to 2 s fixed in `beskid test` (compile/JIT per test), and a target has a
120 s execution budget ("120-second target budget expired", remaining tests reported as
`timed_out`). 50+ tiny tests in one target time out; the same assertions grouped into
~8 tests per target run in about 20 s. Group assertions per test and keep targets under
~40 tests.

Also: test and function names beginning with `host_` fail to parse ("expected Identifier",
the lexer appears to treat `host` as a keyword prefix); test names must be snake_case
without double or trailing underscores, and must be unique per target.
