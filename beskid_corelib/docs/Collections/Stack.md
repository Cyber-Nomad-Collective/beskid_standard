# Core.Collections.Stack

`Stack<T>` owns `T[] storage` and `i64 count`.

`Push` and `Pop` change the stack in place and preserve LIFO order; `Pop` returns the top value as `Option<T>`, `None` when empty. `Peek`, `Count`, and `IsEmpty` read it. `Peek` returns an error for an empty stack. `New<T>` is the module constructor.
