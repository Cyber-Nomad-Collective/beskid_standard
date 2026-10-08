# Web

`corelib_web` is one HTTP client and server facade over HTTP/1.1 (corelib
`Http` codec), HTTP/2, and TLS 1.3 with ALPN. It depends on Foundation,
`corelib_network`, `corelib_http`, `corelib_uri`, `corelib_connect`,
`corelib_x509`, `corelib_tls`, and `corelib_http2`.

## API

- `Web.Send(request, config)` sends a request to an absolute `http://` or
  `https://` URL. `Web.Exchange` also reports the protocol.
- `Web.ServeTls` and `Web.ServePlain` serve connections.
- `Web.WebConfig` sets limits, ALPN, and trust.

## Limits

- One request per connection. There is no connection pool (ruling R14).
- The server serves connections one after another on the calling fiber.
- HTTP/1.0 and close-delimited responses are rejected (ruling R15).
- HTTP/3 is not yet selected by this facade.
