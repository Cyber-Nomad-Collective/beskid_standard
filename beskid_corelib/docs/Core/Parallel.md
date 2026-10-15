# Core.Parallel

`Core.Parallel` runs Beskid code on more than one core. The unit of parallelism is the isolate: a runtime instance with its own heap, garbage collector and fiber scheduler, on its own OS thread. Fibers, channels, mutexes, wait groups and hubs (`Concurrency.*`) stay inside one isolate. Values cross between isolates only through task captures, task results and ports.

Package: `corelib_concurrency`. Modules:

| Module | Contents |
| --- | --- |
| `Core.Parallel` | `Parallel.Scope`, `Parallel.ScopeWith`, `Parallel.IsCancelled`, `Parallel.Of`, `Parallel.OfArray`; the transfer contracts `Transferable`, `Shared`, `Moved`, `Copied` (the marker attributes are declared in `Core.Attributes`) |
| `Core.Parallel.Scopes` | `Scope`, `ScopeOptions`, `Task<T>`, `TaskError`, `TaskFailure`, `ParallelError`, `PipelineStage<T>` |
| `Core.Parallel.Isolate` | `Isolate` (`Current`, `Main`, `Equals`, `Cancel`) |
| `Core.Parallel.Port` | `Port<T>`, `PortError`, `SendOk` |
| `Core.Parallel.ReadOnlyArray` | `ReadOnlyArray<T>`, `Freeze` |
| `Core.Parallel.ParallelSeq` | `ParallelSeq<T>`, `List<T>.Parallel()` |
| `Core.Parallel.Combiners` | `Associative<T>`, `Commutative<T>`, `SumI64`, `SumF64`, `MaxI64`, `MinI64`, `Concat`, `Count` |

## Transfer classes

Every type has one transfer class. The compiler computes it; the markers on a type declare it.

| Class | Meaning | Members |
| --- | --- | --- |
| Shared | Nothing can write it, so several heaps can refer to it. | primitives, `string`, `[Immutable]` types whose fields are Shared, enums whose fields are Shared, `Isolate`, `Port<T>`, `Task<T>`, `ReadOnlyArray<T>` when `T` is Shared |
| Moved | It has one owner; the owner changes at hand-over. | `T[]`, `[Isolated]` types, corelib collections such as `List<T>` |
| Copied | Plain data that is copied at each transfer. | `[Copyable]` types whose fields are Shared or Copied |
| Never | It cannot cross a heap boundary. | function values, `pointer`, `[NeverTransferable]` types (`Fiber<T>`, `Channel<T>`, `Mutex`, `WaitGroup`, `Hub<T>`, `Scope`, sockets), types without a marker |

`Transferable` is Shared, Moved or Copied. Task bodies, port elements and sequence elements must be `Transferable` (E1610 for an element type, E1236 for a capture).

## Fork-join

```beskid
use Core.Results;
use Core.Parallel;
use Core.Parallel.Scopes;

Result<i64, ParallelError> SumTwo() {
    return Parallel.Scope<i64>((Scope s) => {
        Task<i64> left = s.Spawn(() => 20_i64);
        Task<i64> right = s.Spawn(() => 22_i64);
        i64 a = match left.Join() { Result::Ok(v) => v, Result::Error(_) => 0_i64 };
        i64 b = match right.Join() { Result::Ok(v) => v, Result::Error(_) => 0_i64 };
        return Result::Ok(a + b);
    });
}
```

- The scope returns only after every task it started is terminal, on every exit path.
- A failed task (a panic, or a `SpawnTry` body that returned `Error`) cancels its siblings. The scope returns `ParallelError::Failed` with every failure in spawn order.
- `s.Cancel()` cancels every task; the scope then returns `ParallelError::Cancelled`.
- When no pool isolate is free, `Spawn` runs the body on the calling isolate before it returns (elision). Nested scopes therefore never wait for a pool slot.
- `BESKID_ISOLATES_MAX` bounds the live isolates (default: the logical processor count). `ScopeOptions { workers: n, serial: false }` caps one scope; `serial: true` runs every body on the caller in program order.

## Ports and pipelines

`s.Port<T>()` makes a port of capacity 64 that the scope owns; `s.PortWith<T>(n)` sets the capacity. `Send` parks while the port is full, `Receive` parks while it is empty and open, and `TryReceive` never parks. The scope closes its ports when it returns. `s.Isolate(body)` starts a long-lived isolate that serves an inbox port.

A pipeline is a chain of stages connected by ports:

```beskid
Result<i64, ParallelError> Count() {
    return Parallel.Scope<i64>((Scope s) => {
        return s
            .Source((Port<i64> out) => {
                mut i64 i = 1;
                while i <= 1000 { out.Send(i); i = i + 1; }
                return;
            })
            .Stage(4_i64, (n) => n * n)
            .Ordered()
            .Sink((square) => { return; });
    });
}
```

A stage with more than one worker can reorder records; `Ordered()` restores input order.

## Parallel sequences

`values.Parallel()` (or `Parallel.Of(values)`, `Parallel.OfArray(array)`) borrows its source: no element is copied, and the source stays usable. `Where`, `Map`, `Chunk` and `MinChunk` build a plan and run nothing. `Count`, `Collect`, `ForEach`, `Reduce` and `ReduceUnordered` run the plan in one fused pass per chunk.

```beskid
i64 SumOfSquaresOfEvens(List<i64> values) {
    return values.Parallel().Where((x) => x % 2 == 0).Map((x) => x * x).Reduce(0_i64, SumI64 { });
}
```

- Without `Chunk` or `MinChunk`, the sequence starts with one chunk per isolate. A worker splits its remaining range in half when another pool isolate is idle and the range holds at least twice the floor. The floor is the number of elements that the worker processed in its first heartbeat (1 ms), so short bodies get large chunks and long bodies get small ones.
- `Collect` and `Reduce` keep input order. `ReduceUnordered` is the only operation whose combination order depends on scheduling.
- Every chunk of `Reduce` and `ReduceUnordered` starts from the seed, so the seed must be `Shared` or `Copied`. A `Moved` seed is rejected (E1236).
- A combiner is a transferable type that conforms to `Associative<T>` (and `Commutative<T>` for `ReduceUnordered`). The compiler does not prove these claims.
- A plan whose lambdas use no `Port`, no `ReduceUnordered`, no clock, no random source and no I/O gives the serial result on every run and for every isolate count.

## Cost table

| Operation | Cost |
| --- | --- |
| Passing a `Shared` value (capture, result, port) | O(1) transfer; at receive O(roots) to record one foreign entry per root object |
| Passing a `Moved` value (capture, port, pipeline record) | O(1) transfer; plus O(objects in the graph) tracing at send and O(objects) tracing at receive; a `u8[]` of any length is one object |
| Passing a `Copied` value | O(size) copy out and O(size) copy in |
| Task result at join | O(1) for `Shared` and `Moved` (heap adoption); O(size) for `Copied` |
| `ParallelSeq` over `T: Shared` | input by pointer, no copy in; output chunks adopted, one concatenation |
| `ParallelSeq` over `T: Copied` | input chunks copied out once per worker, output chunks copied back |
| `Reduce` | per-worker partial, one combine tree, no element copies beyond the input |
| `s.Spawn(body)` onto a pooled isolate | one spawn message; captures passed per class above |
| New isolate | runtime instance and heap creation; pooled and reused |

Moved hand-over is not free: a `List<Node>` of one million nodes costs two walks of one million objects (one at send, one at receive), not zero. A `u8[]` costs one entry.
