# Core.Threading

`Core.Threading.Thread` exposes one operation: `Yield`, an OS-level scheduler hint. Fibers are the Beskid concurrency model (see the Concurrency package). Corelib does not expose raw OS-thread creation or joining.

## Functions

| Function | Signature | Behavior |
|----------|-----------|----------|
| `Yield` | `unit Yield()` | Calls the runtime `__thread_yield` service to hint the OS scheduler. |

## Yielding

```beskid
Core.Threading.Thread.Yield();
// Hints the OS scheduler. It does not switch to Beskid's cooperative
// scheduler; use Concurrency.Yield for that.
```

## Notes

- `Thread.Yield` and `Concurrency.Yield` are distinct. `Concurrency.Yield` reschedules the current fiber.
- The module is not re-exported from `Prelude.bd`; import `Core.Threading.Thread` explicitly.
