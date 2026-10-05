# Compiler gaps found with beskid 0.5.2

Append: date, slice, symptom, minimal repro, workaround.

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
