# Http2

`corelib_http2` is an HTTP/2 (RFC 9113) client and server with HPACK
(RFC 7541). It maps messages to the corelib `Http.Types` request and response.
It depends on Foundation, `corelib_network`, and `corelib_http`.

## API

- `Http2.Client`: `Open`, `Send`, `Ping`, `Close`.
- `Http2.Server`: `ServeConnection` serves one connection, `AcceptAndServe`
  accepts and serves.
- `Http2.Frame`, `Http2.Settings`, `Http2.Streams`: frames, settings, stream states,
  and flow control.
- `Http2.HpackEncoder` and `Http2.HpackDecoder`: header compression.
- `Http2.MemoryTransport`: an in-memory transport for tests.

## Limits

- Run test targets one at a time. `--all-targets` shares one heap cap across
  targets and can trap with `out_of_memory` (COMPILER-GAPS 9).
- Server push is not supported. The client sends `SETTINGS_ENABLE_PUSH = 0` and
  treats PUSH_PROMISE as a protocol error.
