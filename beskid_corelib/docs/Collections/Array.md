`Collections.Array` defines **`ArrayIter<T>`** and traversal helpers over **`T[]`**.

## Types

```beskid
pub type ArrayIter<T> {
    i64 index,
    i64 length,
}
```

## Functions

| Function | Notes |
|----------|-------|
| `Len<T>(T[] values) -> i64` | Currently invokes **`__panic_str`** (“Array.Len is unavailable until array length builtin is exposed”) and returns `0` only after unreachable panic path—do not call in production until wired. |
| `Iterate<T>(T[] values) -> ArrayIter<T>` | Builds an iterator at index `0` with `length = Len(values)`. |
| `HasNext<T>(ArrayIter<T> it) -> bool` | `it.index < it.length`. |

## Policy

- Prefer language-level array semantics for bounds; once **`Len`** is runtime-backed, iterators stay consistent with that length.
