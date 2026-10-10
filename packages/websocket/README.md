# WebSocket

`corelib_websocket` is a WebSocket (RFC 6455) client and server over TCP or TLS.
It depends on Foundation, `corelib_network`, `corelib_uri`, `corelib_codec`,
`corelib_connect`, `corelib_crypto`, `corelib_x509`, and `corelib_tls`.

## API

- `WebSocket.WsConnection.Open(url, options)` connects a client (`ws://` and `wss://`).
- `Accept` and `AcceptTls` run the server handshake.
- `SendTextOn`, `SendBinaryOn`, `ReceiveOn`, `PingOn`, `CloseOn` exchange messages.
- `DefaultOptions`, `WithProtocols`, `WithOrigin`, `WithMaxMessageBytes`,
  `WithTimeouts`, `WithTls` configure a connection.

## Limits

- No extensions are offered (no permessage-deflate). Messages are capped at
  64 KiB by default (ruling R8).
