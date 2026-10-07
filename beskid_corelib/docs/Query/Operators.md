# Query.Operators

Every operator takes an `ArrayIterator<T>` and works on its remaining elements, starting at the current one.

The 0.5.2 compiler cannot lower lambdas, so there are no predicate or projection callbacks. Selection uses a boolean mask (`Where`) or value comparison (`WhereEquals`, `Distinct`); equality is `==`, which compares primitives and strings by value and other types by identity.

| Function | Result |
|----------|--------|
| `Take(it, n)`, `Skip(it, n)` | First `n` / all but the first `n` remaining elements. |
| `Count(it)`, `IteratorIsEmpty(it)` | Remaining count / whether none remain. |
| `First(it)`, `Last(it)` | `Option<T>`. |
| `ToArray(it)` | Remaining elements as a new array. |
| `Any(it, value)`, `All(it, value)` | Whether any / all remaining elements equal `value` (`All` of nothing is `true`). |
| `Where(it, keep)` | Elements whose position in the `bool[]` mask is `true`. |
| `WhereEquals(it, value)`, `WhereNotEquals(it, value)` | Elements equal / not equal to `value`. |
| `Distinct(it)` | First occurrence of each value, in order. |
| `CountOf(it, value)`, `IndexOf(it, value)` | Occurrences / offset of the first match (`-1` when absent). |
| `Concat(it, tail)`, `Reverse(it)` | Remaining elements followed by `tail` / reversed. |
| `OrderBy(it, ascending)` | Sorted `i64` values via the stable merge sort in `Core.Collections.Sort`. |
| `SumI64`, `SumF64`, `MinI64`, `MaxI64`, `AverageF64` | Numeric aggregates; min, max, and average return `None` when empty. |

```beskid
use Query.ArrayIterator;
use Query.Operators;

i64[] scores = [72_i64, 95_i64, 88_i64];
mut bool[] passed = Array.Empty<bool>();
mut i64 i = 0;
while i < Array.Len<i64>(scores) {
    passed = Array.Append<bool>(passed, Array.Get<i64>(scores, i) >= 80);
    i = i + 1;
}
i64[] passing = Operators.Where<i64>(ArrayIterator.Over<i64>(scores), passed); // 95, 88
```

For sorting other element types by a key, use `Core.Collections.Sort.ByI64Key` and its siblings.
