# Core.Collections.List

`List<T>` owns `T[] storage` and `i64 count`. `Push`, `Pop`, `Get`, `Count`, and `IsEmpty` are owning receiver methods; `New<T>` is the module constructor.

Growth preserves every retained value in order. `Get` returns `Result::Error("index out of range")` when `index < 0` or `index >= Count()`.

## Additional operations

| Method | Behavior |
|--------|----------|
| `TryGet(index)`, `First()`, `Last()` | `Option<T>`; `None` when out of range or empty. |
| `IndexOf(value)`, `Contains(value)` | `==` search; `-1` when absent. |
| `Set(index, value)`, `Insert(index, value)`, `RemoveAt(index)` | `Result<List<T>, CollectionError>`; `IndexOutOfRange(index, count)` on bad input. `Insert` accepts `index == Count()` to append. |
| `Remove(value)` | Removes the first equal element; unchanged when absent. |
| `Reverse()`, `Slice(start, length)`, `Concat(other)`, `Clear()` | New lists; `Slice` clamps to the bounds. |
| `ToArray()` | Copy of exactly `Count()` elements. |

`FromArray<T>(values)` builds a list from an array. Equality uses `==`, which compares primitives and strings by value and other types by identity. Lists are linear values: keep using the returned list.
