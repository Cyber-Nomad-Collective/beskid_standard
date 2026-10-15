# Core.Collections.Sort

Stable bottom-up merge sort (`O(n log n)`) over arrays. Every function returns a new array and leaves its input unchanged.

| Function | Behavior |
|----------|----------|
| `I64(values)`, `F64(values)`, `Strings(values)` | Ascending; f64 NaN sorts last; strings are ordinal (byte-wise), so `"Z"` sorts before `"a"`. |
| `ByI64Key<T>(items, keys)`, `ByF64Key<T>`, `ByStringKey<T>` | Stable sort of any element type by a parallel key array (`keys[i]` belongs to `items[i]`). |
| `OrderByI64(keys)`, `OrderByF64`, `OrderByString` | The sorting permutation itself: `order[i]` is the source index for position `i`. |
| `Permute<T>(items, order)`, `Reverse<T>(items)` | Rearranging helpers. |
| `IsSortedI64`, `IsSortedStrings` | Ascending check. |
| `BinarySearchI64(sorted, value)`, `BinarySearchString` | Index when found, otherwise `-(insertionPoint) - 1`. |

Keyed sorting replaces comparator callbacks, which the 0.5.2 compiler cannot lower:

```beskid
string[] names = ["carol", "al", "bea"];
i64[] lengths = [5_i64, 2_i64, 3_i64];
string[] byLength = Sort.ByI64Key<string>(names, lengths); // al, bea, carol
```

For descending order, `Sort.Reverse` the ascending result (equal keys then appear in reverse insertion order).
