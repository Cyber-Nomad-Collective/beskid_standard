# Core.Collections.Set

`Set<T>` owns `T[] storage` and `i64 count` and uses linear equality scans.

`Add`, `Remove`, `Contains`, `Count`, and `IsEmpty` are owning receiver methods. Duplicate additions do not change storage semantics or count, and removal preserves every other retained value. `New<T>` is the module constructor.

## Set algebra

`Union(other)`, `Intersect(other)`, `Difference(other)`, and `IsSubsetOf(other)` keep this set's order. `ToArray()` copies the members; `FromArray<T>(values)` keeps the first occurrence of each duplicate.
