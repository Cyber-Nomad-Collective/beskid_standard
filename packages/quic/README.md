# Quic

`corelib_quic` is QUIC version 1 (RFC 9000, 9001, 9002) over
`Network.UdpSocket`. It depends on Foundation, `corelib_concurrency`,
`corelib_network`, `corelib_codec`, `corelib_crypto`, and `corelib_tls`.

## API

- `Quic.QuicEndpoint`: `Bind`, `Connect`, `Accept`, `OpenStream`,
  `AcceptStream`, `Read`, `Write`, `Finish`, `Reset`, `StopSending`, `Close`.
- `Quic.QuicConfig`: transport parameters and TLS configuration.
- `Quic.QuicConnection`, `QuicRecovery`, `QuicCongestion`: the connection state
  machine, loss recovery, and congestion control.

## Limits

- No 0-RTT. Active migration is disabled (`disable_active_migration`).
