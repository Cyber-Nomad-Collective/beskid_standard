# Core.Collections.Queue

`Queue<T>` owns `T[] storage`, `i64 head`, and `i64 count`.

`Enqueue` and `Dequeue` change the queue in place and preserve FIFO order; `Dequeue` returns the front value as `Option<T>`, `None` when empty. `Peek`, `Count`, and `IsEmpty` read it. `Peek` returns an error for an empty queue. `New<T>` is the module constructor.
