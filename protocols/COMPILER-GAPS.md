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
