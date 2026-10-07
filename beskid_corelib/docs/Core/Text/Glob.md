# Core.Text.Glob

Shell-style wildcard matching on bytes.

| Syntax | Matches |
|--------|---------|
| `*` | any run of characters (`MatchPath`: within one segment) |
| `?` | one character (`MatchPath`: never `/`) |
| `**` | `MatchPath` only: zero or more whole segments (`src/**/*.bd`) |
| `[abc]`, `[a-z]`, `[!x]`, `[^x]` | one listed / ranged / unlisted character; a leading `]` is a member |
| `\x` | literal `x` |

`Match(pattern, text)` treats text as plain; `MatchPath(pattern, path)` treats `/` as a separator. `HasWildcards(pattern)` tells literal paths from patterns.
