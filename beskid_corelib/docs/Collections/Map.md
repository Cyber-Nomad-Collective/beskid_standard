# Core.Collections.Map

`Map<TKey, TValue>` owns `MapEntry<TKey, TValue>[] entries` and `i64 count`. It uses linear key lookup.

`Insert`, `Remove` and `Clear` change the map in place; `Remove` returns `false` when the key is absent. `Get`, `ContainsKey`, `Count`, and `IsEmpty` read it. Inserting an existing key replaces its value without changing count. Removing a key preserves all remaining entries. `New<TKey, TValue>` is the module constructor.

## Additional operations

`TryGet(key) -> Option<TValue>`, `GetOr(key, fallback)`, `Keys()`, `Values()`, `Entries()` (copies in insertion order). For maps that grow beyond a handful of entries, prefer the hashed [StringMap and I64Map](./HashMaps.md).
