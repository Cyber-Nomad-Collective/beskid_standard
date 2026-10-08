# Beskid networking protocols program

Goal: realize the agreed post-0.5 networking order entirely in Beskid, built and
tested with the released beskid 0.5.2 CLI, parallel to the v0.6 release work.

1. URI parser, reusable codecs, Happy Eyeballs connect.
2. TLS 1.3 as a wrapper around `Core.IO.Stream`, with explicit trust and ALPN policy.
3. HTTP/2 behind the same request/response API as corelib `Http`, and WebSocket.
4. QUIC, then HTTP/3 with QPACK.
5. HTTP/2 and QUIC reuse the existing runtime network layer (`Network.TcpStream`,
   `Network.UdpSocket`, `Network.Dns`, Foundation `Core.IO`). No second reactor,
   no native socket API, no new runtime builtins.

User rule: implementation first; OpenSpec, docs and website come later.

Sources of the order: `docs/research/2026-09-22-v05-network-protocol-candidates.md`
and `docs/superpowers/specs/2026-09-22-future-ready-networking-design.md` in the
root beskid repository.

## Where the packages live

The 0.5.2 CLI authorized corelib runtime services (`__panic`, network builtins,
...) only when the corelib tree was byte-identical to its embedded bundle, so
the packages were first developed under `protocols/` against an unmodified
0.5.2 corelib copy. Compiler 0.5.3 grants authority per canonical service file,
so the packages now live in `packages/<pkg>/` of the corelib repository and are
registered in the `beskid_corelib/corelib.bproj` aggregate (ruling R21).
The program notes, gap log, and repros are in `docs/networking/`.

## Environment (mandatory)

```bash
export BESKID_RUNTIME_PREFIX=<0.5.3 runtime kit>   # builder: /workspace/v053-kit3
unset BESKID_CORELIB_ROOT
beskid test --project packages/<pkg>/tests --target <Target> --plain
```

- CLI: beskid 0.5.3 (builder: `/target/compiler-v053/release/beskid_cli`).
  The 0.5.2 CLI cannot build the relocated packages: they depend on in-tree
  corelib packages, which 0.5.2 does not authorize.
- Prefer one `--target` per run. `--all-targets` shares one heap cap across
  targets (COMPILER-GAPS 9), so per-target runs are the acceptance evidence.
- Delete `tests/obj` if a build behaves inconsistently. Do not commit `obj/` or
  `Project.lock`.

## Dependency scheme

- A package `packages/<pkg>/corelib_<pkg>.bproj` depends on `corelib_foundation`
  and on the exact sibling packages whose modules its `src` imports
  (`corelib_concurrency`, `corelib_network`, `corelib_http`, `corelib_<pkg>`).
  It never depends on the aggregate, because the aggregate depends on it.
- `corelib_crypto` carries the optional OpenSSL 3 provider in process (R27);
  there is no separate native package.
- A test or interop project depends only on the aggregate
  (`dependency "corelib"`, path to `beskid_corelib`), like `corelib_tests`.

## Layout

Each package `packages/<pkg>/` has `corelib_<pkg>.bproj`, `src/<Module>.bd`
plus `src/<Module>/*.bd`, and a test project `tests/<pkg>_tests.bproj` with
targets in `tests/src/*.bd`. Add a test target per area (keep targets small:
one failed assertion traps the whole target process, so later tests in that
target do not run).

| Package | Module | Depends on (besides foundation) | Scope |
| --- | --- | --- | --- |
| uri | `Uri` | - | RFC 3986 parse/format, normalization, reference resolution, percent-encoding, authority/host/port, IPv4/IPv6 literals |
| codec | `Codec` | - | Bounded byte primitives: big-endian ints, QUIC varint, length-prefixed vectors, bounded line reader, incremental `BufferedReader`/writer over `Core.IO` |
| connect | `Connect` | concurrency, network | RFC 8305 Happy Eyeballs: resolve, interleave families, staggered attempts (250 ms), cancel losers, typed attempt errors |
| crypto | `Crypto` | - | SHA-256/384/512, HMAC, HKDF, ChaCha20-Poly1305, AES-128/256-GCM, X25519, P-256 ECDH/ECDSA, RSA PKCS#1 v1.5/PSS verify, constant-time compare, OS entropy |
| x509 | `X509` | crypto | DER/ASN.1, PEM, certificate parsing, chain building, signature check, validity, name constraints basics, RFC 6125 hostname verification, trust store |
| tls | `Tls` | network, codec, crypto, x509 | TLS 1.3 (RFC 8446) client and server, `TlsStream` implementing `Core.IO.Stream`, explicit trust/hostname/ALPN policy, no insecure default |
| http2 | `Http2` | network, http | RFC 9113 frames, HPACK (RFC 7541), stream states, flow control, settings, client and server, mapped to corelib `Http.Types` Request/Response |
| websocket | `WebSocket` | network, uri, codec, connect, crypto, x509, tls | RFC 6455 opening handshake over HTTP/1.1, framing, masking, fragmentation, ping/pong, close |
| quic | `Quic` | concurrency, network, codec, crypto, tls | RFC 9000/9001/9002 over `Network.UdpSocket`: packets, protection, TLS handshake, streams, flow control, loss recovery, congestion control |
| http3 | `Http3` | concurrency, network, http, uri, codec, tls, http2, quic | RFC 9114 and QPACK (RFC 9204) |
| web | `Web` | network, http, uri, connect, x509, tls, http2 | One client/server facade over HTTP/1.1, HTTP/2, HTTP/3 with ALPN selection |

## Beskid 0.5.2 language facts (verified)

- Primitive types: `bool i32 i64 u32 u8 pointer word f64 char string unit never`.
  No `u16`, no `u64`. Integer literal suffixes: `_i32 _i64 _u32 _u8`; hex `0x..`.
  Use conversion calls such as `u32(x)`, `u8(x)`, `i64(x)`.
- Operators: `+ - * / % << >> & |`, comparison, `&& || !`. There is no `^`
  and no `~`. XOR: `(a | b) - (a & b)`. NOT for u32: `0xFFFFFFFF_u32 - a`.
- `&` and `|` bind looser than `==`: always parenthesize, `(a & m) == v`.
- Arithmetic wraps for u32, u8 and i64 (add, sub, mul). `>>` is a logical shift
  even on `i64`. Shifts by >= width are not defined; avoid them.
- Arrays: `u8[]`; `Core.Bytes.Slice.New(n)`, `Slice.Len`, `Slice.Copy`;
  `Core.Collections.Array.Append<T>(arr, v)` on `mut` arrays.
- Tests: `test name { ... }`; `Testing.Assert.Equal<T>(actual, expected, "because")`,
  `Assert.True/False(cond, "because")`, `Assert.Fail("...")`. Do not call
  `__panic*` from package or test code (corelib-only service).
- Extern C: `[Extern(Abi:"C", Library:"libc")] pub contract X { i32 f(i64 a); }`
  (see corelib `Core/Threading/Thread.bd`).
- Buffers: `Slice.New(n)` appends n times (cost grows with n, sometimes
  quadratically) and one array near 180 KiB, or several live 64 KiB arrays, traps
  `out_of_memory`. Allocate record-sized buffers once and reuse them; use the
  in-place crypto APIs (`SealInto`/`OpenInto`); never buffer a whole body or
  stream; keep windows and flow-control limits at or below 64 KiB by default.
- Struct fields cannot be `mut`; keep mutable state in array fields or pass `mut`
  values. A `return` inside a block match arm is not treated as diverging.
- Extern parameters must be primitives (`i32 i64 ...`, no `u32`, no arrays).
- Runtime concurrency limits (0.5.2): at most 64 channels per process and closed
  channels are never freed, so never create a channel per connection, stream or
  request. Coordinate with preallocated flag arrays + `Fiber.Join` + short polls
  (see `packages/connect/src/Connect/Engine.bd`). A cancelled fiber stops at
  its next wait without cleanup and its children are not cancelled: always give
  network operations deadlines. The socket table has 256 slots.
- Identifiers `host`, `launch` and names starting with `spawn` are reserved by
  the parser. `use` binds the last path segment: avoid submodule names that
  collide with corelib ones (`Errors`, `Types`, `Codec`, ...); prefix them.
- See `docs/networking/COMPILER-GAPS.md` before writing closures, nested generic
  matches, or matches on struct fields of `Option` type.
- A contract value (e.g. `Core.IO.Stream`) cannot be a struct field (ICE), and a
  method forwarding `this` plus a contract argument fails. Pass the transport to
  module functions on every call (`Codec.Buffered.ReadLine(b, source, max)`), or
  hold a concrete `TcpStream`, or an enum of concrete transports.
- `this.Other()` inside a method is an ICE: write module-level functions and thin
  wrapper methods. Field access on a call result (`F(x).f`) and `match` on a
  nested field path are ICEs: bind a local first.
- Narrowing `u8(i64)`/`u32(i64)` does not wrap: mask first. No `\n` escape.
  `Core.Output.Write` traps inside `beskid test`.
- Each test costs 1-2 s of JIT; a target has a 120 s budget
  (`--target-timeout 600` on a loaded host). Keep targets under ~40 tests.
- Available uri/codec: `Uri.Parse`, `Uri.Resolve`, `Uri.Scheme.AuthorityOf`,
  `HostHeader`; `Codec.Cursor`, `Codec.Builder` (length back-patch), `Codec.Be`,
  `Codec.Varint` (QUIC), `Codec.Vec` (TLS vectors), `Codec.Buffered`, `Codec.Hex`.
- Available http2: HPACK (`Http2.Hpack*`).
- Available connect: `Connect.ConnectHost(host, port, policy)` and
  `Connect.ConnectAddresses(addresses, policy)` return `TcpStream`.
- Available crypto (`packages/crypto`, 18 targets green): `Crypto.PkAdapters` (VerifyRsaPss/Pkcs1Message, SignEcdsaP256*, VerifyEcdsaP256Message), X25519, P256, Ecdsa, Rsa verify, SHA-256/384/512, HMAC, HKDF with
  `ExpandLabel`/`DeriveSecret`, ChaCha20-Poly1305, AES-128/256-GCM, AES block,
  ChaCha20 block (QUIC header protection), ConstantTime, `Entropy.Fill`.
- Idiom reference: corelib `packages/http/src/Http/*.bd`, `packages/network/src/Network/*.bd`,
  tests in `beskid_corelib/tests/corelib_tests/src/{http,network}`.

## Working rules for slices

- Work in your own git worktree and branch (given in your brief). Commit there in
  small steps. Never push, never merge, never stash.
- Test first where practical: use RFC test vectors (RFC 3986 section 5.4,
  RFC 7541 appendix C, RFC 8448, RFC 9001 appendix A, NIST/Wycheproof vectors, ...).
- Fail closed with typed error enums. Bound every buffer and count.
- When the 0.5.2 compiler rejects valid code, reduce it to a minimal repro,
  append it to `docs/networking/COMPILER-GAPS.md` (symptom, repro, workaround), and
  work around it in source. Do not stop the slice for a workaround-able gap.
- Report: what is implemented, test targets with pass counts, gaps, open items.
