# Core.Collections.PriorityQueue

`PriorityQueue<T>` is a binary min-heap ordered by an `i64` priority. The smallest priority is served first and equal priorities are served in insertion order. `Push` and `Pop` are `O(log n)`; `Peek` and `PeekPriority` are `O(1)` and return `Option`.

```beskid
use Core.Collections.PriorityQueue;

PriorityQueue<string> jobs = PriorityQueue.New<string>();
jobs.Push("rebuild index", 5);
jobs.Push("serve request", 1);
// jobs.Peek() is Some("serve request")
Option<string> next = jobs.Pop();
```

`Push` and `Pop` change the queue in place. `Pop` returns the removed item, or `None` when the queue is empty. Use negated priorities for max-first order.
