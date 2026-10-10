# Uri

`corelib_uri` parses, formats, normalizes, and resolves URI references (RFC 3986).
It depends only on Foundation.

## API

- `Uri.Parse.Parse(text)` parses an absolute URI. `Uri.Parse.ParseReference(text)`
  parses a relative or absolute reference. `ParseWith` sets a maximum length.
- `Uri.Format.Format(uri)` writes a URI back to text.
- `Uri.Normalize.Normalize(uri)` and `NormalizeForScheme(uri)` apply syntax-based
  and scheme-based normalization. `Equivalent(a, b)` compares normalized forms.
- `Uri.Resolve.Resolve(base, reference)` resolves a reference (RFC 3986 section 5).
- `Uri.Pct` encodes and decodes percent-encoding. `Uri.Host` parses registered
  names and IPv4 and IPv6 literals. `Uri.Scheme` gives default ports.
- Every failure is a typed `Uri.Errors.UriError`.

## Limits

- IPv4 hosts must be strict dotted decimal. The parser rejects `127.1`,
  `0x7f.1`, and `2130706433` (ruling R4).
- The parser does not apply WHATWG URL rules or IDNA conversion.
