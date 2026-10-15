# Hash maps: StringMap, I64Map, HashTable, Hash

`Core.Collections.StringMap<V>` and `Core.Collections.I64Map<V>` are hash maps with expected O(1) `Get`, `Insert`, and `Remove`. Use them instead of the linear `Map<TKey, TValue>` when a map can grow beyond a handful of entries.

| Method | Behavior |
|--------|----------|
| `Count()`, `IsEmpty()` | Size. |
| `ContainsKey(key)` | Membership. |
| `Get(key) -> Option<V>`, `GetOr(key, fallback)` | Lookup. |
| `Insert(key, value)` | Adds or replaces; returns the updated map. |
| `Remove(key)` | Removes when present; returns the updated map. |
| `Keys()`, `Values()` | Copies in iteration order. |

```beskid
use Core.Collections.StringMap;

mut StringMap<i64> counts = StringMap.New<i64>();
counts = counts.Insert("beskid", 1);
counts = counts.Insert("beskid", counts.GetOr("beskid", 0) + 1);
```

Maps are linear values: keep using the returned map. Iteration order is insertion order until the first removal, which moves the last entry into the removed position.

## HashTable

`Core.Collections.HashTable<K, V>` is the open-addressing engine behind both maps: dense parallel key, value, and hash arrays plus a power-of-two slot index with linear probing, kept at or below a 3/4 load factor. Its module functions take the key's hash from the caller, so any key whose `==` is value equality works. Combine field hashes for composite keys:

```beskid
i64 hash = Hash.Combine(Hash.String(name), Hash.I64(version));
table = HashTable.Insert<string, i64>(table, name, hash, version);
```

## Hash

| Function | Behavior |
|----------|----------|
| `String(text)` | 64-bit FNV-1a over the UTF-8 bytes. |
| `I64(value)` | SplitMix64 finalizer. |
| `Combine(seed, value)` | Order-dependent mixing for composite keys. |
| `Xor(a, b)`, `ShiftRightLogical(value, bits)` | Bit helpers; the language has no `^` or logical shift operator. |

These hashes are deterministic and not designed for adversarial input.
