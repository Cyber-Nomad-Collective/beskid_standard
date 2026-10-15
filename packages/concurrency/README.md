# corelib_concurrency

Concurrency for the Beskid standard library.

- `Concurrency.*`: cooperative fibers inside one isolate (`Fiber`, `Channel`, `Hub`, `Mutex`, `WaitGroup`). These handles are `[NeverTransferable]`: they never leave the isolate that created them.
- `Core.Parallel.*`: parallelism across isolates. An isolate is a runtime instance with its own heap, collector and scheduler on its own OS thread. `Parallel.Scope` runs fork-join tasks, `Port<T>` connects isolates, `PipelineStage<T>` chains ports into pipelines, and `ParallelSeq<T>` runs data-parallel operators over a borrowed list or array. See `beskid_corelib/docs/Core/Parallel.md` for the transfer rules and the cost table.

Corelib exposes no raw OS-thread spawn: `Core.Threading.Thread.Yield` (foundation) is the only OS-thread operation, and isolate threads belong to the runtime.

Depends on `corelib_foundation`. The aggregate `corelib` package re-exports the supported surface.
