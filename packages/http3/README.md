# Http3

`corelib_http3` is HTTP/3 (RFC 9114) with QPACK (RFC 9204) over `corelib_quic`.
It depends on Foundation, `corelib_concurrency`, `corelib_network`,
`corelib_http`, `corelib_uri`, `corelib_codec`, `corelib_tls`, `corelib_http2`,
and `corelib_quic`.

## API

- `Http3.H3Client.ConnectQuic(address, port, tls, config, timeoutMillis)` connects and `Send` sends
  a request. `Poll` and `Close` drive and end the connection.
- `Http3.H3Server.ListenQuic` listens. `AcceptQuic`, `NextRequest`, `Respond`,
  and `Shutdown` serve requests.
- `Http3.H3Quic.QuicLink` is the transport (`Memory` or `Quic`, ruling R17).

## Limits

- Only ALPN `h3` is offered or accepted (ruling R18).
- Addresses are IP literals. Name resolution is the caller's task.
- DATA frames are at most 4 KiB (ruling R19).
