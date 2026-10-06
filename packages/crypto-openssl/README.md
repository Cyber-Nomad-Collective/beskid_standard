# CryptoOpenSsl

`corelib_crypto_openssl` is an opt-in native provider for `corelib_crypto`. It
calls OpenSSL 3 `libcrypto.so.3`. It depends on Foundation and `corelib_crypto`.

The package is not part of the `corelib` aggregate. Add it as a separate
dependency only when the target host has OpenSSL 3 (ruling R20).

## API

- `CryptoOpenSsl.NativeSha256`, `NativeSha512`, `NativeHmac`: one-shot hashes and HMAC.
- `CryptoOpenSsl.NativeAesGcm`, `NativeChaCha20Poly1305`: `Seal`, `Open`,
  `SealInto`, and `OpenInto` with the same shape as the `Crypto` modules.
- `CryptoOpenSsl.Provider.SelfTest()` compares the native provider with the
  pure provider. `Provider.Select()` returns `Native` or `Pure`. Set
  `BESKID_CRYPTO_PROVIDER=pure` to force the pure provider.

## Limits

- Linux only. A program that depends on this package does not load on a host
  without `libcrypto.so.3`, even when it does not call the provider
  (COMPILER-GAPS NATIVE1).
- Run its tests on a Linux host with OpenSSL 3.
