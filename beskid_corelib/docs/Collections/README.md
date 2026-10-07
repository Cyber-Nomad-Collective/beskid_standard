# Core.Collections

`Core.Collections` is the only public namespace for the array-backed collection family. The former `Collections.*` path is not declared or aliased.

All receiver operations are defined on their owning public types. Modules retain only constructors and genuine array namespace helpers.

## Modules

- [Array](./Array.md) — typed arrays, direct bounds semantics, rooted growth, and iteration.
- [List](./List.md) — ordered growable values.
- [Map](./Map.md) — key/value entries with linear lookup.
- [Set](./Set.md) — unique values with linear membership.
- [Queue](./Queue.md) — FIFO values.
- [Stack](./Stack.md) — LIFO values.
- [Sort](./Sort.md) — stable sorting, keyed ordering, and binary search.
- [StringMap, I64Map, HashTable, Hash](./HashMaps.md) — hashed maps with expected O(1) operations.
- [PriorityQueue](./PriorityQueue.md) — `i64`-priority min-heap.

Index- and key-based failures (including `List.Get`, `Map.Get`, `Queue.Peek`, and `Stack.Peek`) use the typed `CollectionError` (`IndexOutOfRange(index, count)`, `KeyNotFound`, `Empty`).
