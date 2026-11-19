# Core.Collections.Set

`Set<T>` owns `T[] storage` and `i64 count` and uses linear equality scans.

`Add` and `Remove` change the set in place and return `false` when nothing changed. `Contains`, `Count`, and `IsEmpty` read it. Duplicate additions do not change count, and removal preserves every other retained value. `New<T>` is the module constructor.

## Set algebra

`Union(other)`, `Intersect(other)`, `Difference(other)`, and `IsSubsetOf(other)` keep this set's order. `ToArray()` copies the members; `FromArray<T>(values)` keeps the first occurrence of each duplicate.
