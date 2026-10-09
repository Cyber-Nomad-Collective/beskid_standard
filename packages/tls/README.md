# Tls

`corelib_tls` is a TLS 1.3 (RFC 8446) client and server. It depends on
Foundation, `corelib_network`, `corelib_codec`, `corelib_crypto`, and `corelib_x509`.

## API

- `Tls.Connect(tcp, config, deadline)` runs the client handshake over a
  `Network.Tcp.TcpStream`. `Tls.Accept(tcp, config, deadline)` runs the server
  handshake. On failure the TCP stream is closed and a typed error is returned.
- `Tls.TlsStream` implements `Core.IO.Stream`.
- `Tls.TlsConfig.Client` and `Server` build the configuration. Trust, host name,
  and ALPN policy are explicit. `WithTrustStore` sets the trust anchors.

## Limits

- TLS 1.3 only. A TLS 1.2 ServerHello is refused. There is no PSK, no
  session resumption, and no 0-RTT.
- There is no insecure default. `AcceptAnyCertificateForTestsOnly` is for tests.
