# X509

`corelib_x509` parses and validates X.509 certificates (RFC 5280). It depends
on Foundation and `corelib_crypto`.

## API

- `X509.Der` and `X509.Pem`: strict DER and PEM decoding.
- `X509.Certificate`: certificate parsing.
- `X509.TrustStore`: trust anchors (`Empty`, `FromPem`, `FromFile`, `AddPem`,
  `SystemBundlePath`).
- `X509.Verify.Verify(chain, store, options)`: path building, signature checks,
  validity, and name constraints. `ServerOptions` sets the server profile.
- `X509.Hostname.VerifyHostname(cert, name)`: host name verification (RFC 9525).

## Limits

- RSA keys must have at least 2048 bits (ruling R6).
- Revocation (CRL, OCSP) is not checked.
- Negative serial numbers are rejected. Trailing zero bits in keyUsage and an
  explicit `critical FALSE` are accepted (ruling R7).
