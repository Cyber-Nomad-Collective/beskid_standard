# Crypto

`corelib_crypto` is the cryptography package for TLS 1.3, QUIC, and X.509. It
depends only on Foundation. The algorithms are pure Beskid (CLIF kernels), and an
in-process native provider (OpenSSL 3 libcrypto) serves the hot symmetric calls
when the host has it (ruling R27).

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
- `Crypto.Provider` selects the provider: `Current()`, `IsNative()`,
  `SelfTest()`, `NativeAvailable()`, and `ForcePure(bool)`.

## Providers (ruling R27)

`Crypto.Native` declares OpenSSL 3 `libcrypto.so.3` as an optional extern
contract (compiler 0.5.3). A program that uses `corelib_crypto` loads on every
host; where the library or one of its symbols is missing,
`LibCrypto.Available()` is false and every call stays on the pure kernels.

The provider is selected once per process. It is `Pure` when the library is
absent, when `BESKID_CRYPTO_PROVIDER=pure` is set, or when the known-answer
self-test fails. Otherwise it is `Native`. The self-test result is cached in the
process environment as `BESKID_CRYPTO_PROVIDER_STATE`.

The native provider serves the one-shot `Sha256.Hash`, `Sha512.Hash512` and
`Hash384`, `Hmac.Compute` and `Hmac.Digest` (and through them `Hkdf`), and the
AEADs `AesGcm` and `ChaCha20Poly1305`. An `AesGcmKey` keeps the provider that
was selected when the key was created (`AesGcm.UsesNative`). The public API and
results are the same for both providers, with one difference: when a tag does
not verify, the native open zeroes the output range (OpenSSL decrypts before it
verifies), and the pure open writes nothing. A native failure outside tag
verification returns `CryptoError.ProviderFailed` with the output zeroed.
Streaming hash and HMAC states, public-key algorithms, raw AES and ChaCha20
blocks (QUIC header protection), and inputs of 2^30 bytes or more always use the
pure kernels.

Run the test targets once with `BESKID_CRYPTO_PROVIDER=pure` to cover the pure
kernels on a host that has OpenSSL 3. The `Provider` and `NativeBench` targets
compare the providers and need OpenSSL 3.

## Limits

- AES uses vector-permute AES and GHASH uses a constant-time 64-bit multiply
  (ruling R10). There is no hardware AES or carry-less multiply.
- RSA supports verification only. Certificate keys must have 2048 bits or more.
- `Crypto.Entropy` names libc as `libc.so.6` (Linux) and `libc` (macOS). It needs
  compiler 0.5.3 or later for an AOT link on macOS (COMPILER-GAPS WEB4).
- The native provider is Linux only for now (`libcrypto.so.3`); macOS
  CommonCrypto is not wired. Windows AOT targets reject optional extern
  contracts, so `corelib_crypto` does not link for Windows AOT.
- See `BENCHMARKS.md` for measured throughput.
