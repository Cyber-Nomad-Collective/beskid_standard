# Codec

`corelib_codec` gives bounded byte primitives for TLS, HTTP/2, and QUIC.
It depends only on Foundation.

## API

- `Codec.Be`: big-endian integer read and write.
- `Codec.Varint`: QUIC variable-length integers (RFC 9000 section 16).
- `Codec.Cursor`: a bounds-checked read cursor over a byte slice.
- `Codec.Vec`: length-prefixed vectors (TLS style, 1 to 3 byte lengths).
- `Codec.Builder`: an append-only byte builder.
- `Codec.Line`: a bounded line reader.
- `Codec.Buffered`: an incremental reader over `Core.IO`
  (`New`, `Fill`, `Peek`, `ReadExact`, `ReadLine`, `ReadUntil`, `Skip`).
- `Codec.Hex`: hex encode and decode for tests and diagnostics.

## Limits

- Every read checks bounds. Every failure is a typed `Codec.Errors.CodecError`.
- Buffers have fixed caps. The codec does not grow a buffer without a limit.
