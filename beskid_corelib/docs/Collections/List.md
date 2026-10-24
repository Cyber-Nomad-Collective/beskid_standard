# Core.Collections.List

`List<T>` owns `T[] storage` and `i64 count`. `New<T>` is the module constructor.

A list is a value. Assigning a list to a binding, a field or an array element, passing it to a parameter that is not `mut`, returning it, capturing it in a closure, binding it in a `for` loop or taking it out of a `Result` with `?` gives the new name its own list. The copy is copy-on-write: the two lists share the backing array until one of them changes, and that list copies the array first. A write through one list is never visible through another, and read-only use copies no elements. A `mut List<T>` parameter shares the caller's list, so the callee can change it in place.

```beskid
use Core.Collections.List;

List<string> items = List.New<string>();
items.Push("milk");
List<string> copy = items;
copy.Push("bread");
// items.Count() is 1, copy.Count() is 2
```

Growth preserves every retained value in order. `Get` returns `Result::Error("index out of range")` when `index < 0` or `index >= Count()`.

## Operations that change the list in place

| Method | Behavior |
|--------|----------|
| `Push(value)` | Appends `value`. |
| `Pop()` | Removes the last element and returns it as `Option<T>`; `None` when empty. |
| `Set(index, value)`, `Insert(index, value)` | `Result<unit, CollectionError>`; `IndexOutOfRange(index, count)` on bad input. `Insert` accepts `index == Count()` to append. |
| `RemoveAt(index)` | Removes the element and returns it as `Result<T, CollectionError>`. |
| `Remove(value)` | Removes the first equal element; returns `false` when absent. |
| `Clear()` | Removes every element. |

## Operations that read the list

| Method | Behavior |
|--------|----------|
| `Count()`, `IsEmpty()`, `Get(index)` | Size and checked access. |
| `TryGet(index)`, `First()`, `Last()` | `Option<T>`; `None` when out of range or empty. |
| `IndexOf(value)`, `Contains(value)` | `==` search; `-1` when absent. |
| `Reverse()`, `Slice(start, length)`, `Concat(other)` | New lists; `Slice` clamps to the bounds. |
| `ToArray()` | A copy of exactly `Count()` elements. |
| `Copy()` | A copy-on-write copy of the list (the compiler calls it for every new name). |

`FromArray<T>(values)` builds a list from an array. Equality uses `==`, which compares primitives and strings by value and other types by identity.
