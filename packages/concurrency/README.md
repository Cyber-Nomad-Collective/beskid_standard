# corelib_concurrency

Cooperative concurrency primitives for the Beskid standard library (`Fiber`, channels). Fibers are the Beskid concurrency model; corelib exposes no raw OS-thread spawn. `Core.Threading.Thread.Yield` (foundation) is the only OS-thread operation.

Depends on `corelib_foundation`. The aggregate `corelib` prelude re-exports the supported surface.
