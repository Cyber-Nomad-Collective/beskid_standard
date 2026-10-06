# Crypto

`corelib_crypto` is a pure Beskid cryptography package for TLS 1.3, QUIC, and
X.509. It depends only on Foundation.

## API

- Hashes: `Crypto.Sha256`, `Crypto.Sha512` (also SHA-384), `Crypto.Sha1`
  (WebSocket handshake only).
- MAC and KDF: `Crypto.Hmac`, `Crypto.Hkdf`.
- AEAD: `Crypto.AesGcm` (`New`, `Seal`, `Open`, `SealInto`, `OpenInto`),
  `Crypto.ChaCha20Poly1305`.
- Key exchange and signatures: `Crypto.X25519`, `Crypto.P256`, `Crypto.Ecdsa`
  (`Sign`, `Verify`, DER forms), `Crypto.Rsa` (PKCS #1 v1.5 and PSS verify).
- `Crypto.ConstantTime` compares bytes in constant time.
- `Crypto.Entropy.Fill` and `Bytes` read the operating-system CSPRNG
  (`getentropy`). There is no fallback generator.

## Limits

- AES uses vector-permute AES and GHASH uses a constant-time 64-bit multiply
  (ruling R10). There is no hardware AES or carry-less multiply.
- RSA supports verification only. Certificate keys must have 2048 bits or more.
- `Crypto.Entropy` names libc as `libc.so.6` (Linux) and `libc` (macOS). It needs
  compiler 0.5.3 or later for an AOT link on macOS (COMPILER-GAPS WEB4).
- See `BENCHMARKS.md` for measured throughput.
