# Core.Collections.PriorityQueue

`PriorityQueue<T>` is a binary min-heap ordered by an `i64` priority. The smallest priority is served first and equal priorities are served in insertion order. `Push` and `Pop` are `O(log n)`; `Peek` and `PeekPriority` are `O(1)` and return `Option`.

```beskid
use Core.Collections.PriorityQueue;

mut PriorityQueue<string> jobs = PriorityQueue.New<string>();
jobs = jobs.Push("rebuild index", 5);
jobs = jobs.Push("serve request", 1);
// jobs.Peek() is Some("serve request")
jobs = jobs.Pop();
```

`Pop` on an empty queue returns it unchanged. Use negated priorities for max-first order. Queues are linear values: keep using the returned queue.
