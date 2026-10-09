# Query

**Query** modules iterate and combine array-backed sequences.

- **`Query.Iterator`**: the `Iterator<T>` contract (`Current() -> Option<Item>`, `MoveNext() -> This`).
- **`Query.ArrayIterator`**: the array implementation, plus the module functions `Over`, `Current`, `MoveNext`, `Remaining`, and `Reset`.
- **`Query.Operators`**: combinators over the remaining elements of an `ArrayIterator`; see [Query.Operators](./Operators.md).

Optional results use `Core.Optional.Option`.
