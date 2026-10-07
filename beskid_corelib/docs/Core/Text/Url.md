# Core.Text.Url

RFC 3986 URIs. Import `Core.Text.Url`; types are `Url.Url`, `Url.UrlError`, and `Url.QueryParam`.

`Parse(text)` splits a URI or relative reference into `scheme`, `userInfo`, `hostname` (IPv6 literals keep their brackets), `port` (`-1` when absent), `path`, `query`, and `fragment`, with `hasAuthority`, `hasQuery`, and `hasFragment` distinguishing empty from missing parts. Components are not decoded; `Format(url)` recomposes them.

| Function | Behavior |
|----------|----------|
| `PercentDecode(text, plusIsSpace)` | Decodes `%XX`; optional `+` as space (HTML forms). |
| `PercentEncode(text, keep)` | Encodes everything except `A-Z a-z 0-9 - . _ ~` and the bytes in `keep`. |
| `QueryParams(query)` | Ordered, decoded `key=value` pairs; a bare key has an empty value. |
| `Resolve(base, reference)` | RFC 3986 section 5.2.2 reference resolution. |
| `RemoveDotSegments(path)` | RFC 3986 section 5.2.4. |

The field is `hostname` because `host` is a reserved word in Beskid.
