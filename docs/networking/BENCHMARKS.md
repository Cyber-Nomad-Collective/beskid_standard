# Networking benchmarks

Machine: NixOS builder container (AMD Ryzen 7 7700, shared; load 5-20 during the runs).
Compiler 0.5.3 CLI (JIT, Cranelift `opt_level=speed`), runtime kit `v053-kit3`, one run per
row. Client and server are fibers of one process on one thread, so a transfer pays for both
sealing and opening on one core, and the runtime network layer (`Network.TcpStream`,
`Network.UdpSocket`) is shared by both ends.

Targets (each prints `BENCH` lines):

```bash
beskid test --project packages/tls/tests   --target TlsBench        --plain --target-timeout 3000
beskid test --project packages/tls/tests   --target TlsMicroBench   --plain --target-timeout 3000
beskid test --project packages/http2/tests --target Http2Bench      --plain --target-timeout 3000
beskid test --project packages/quic/tests  --target QuicBench       --plain --target-timeout 3000
beskid test --project packages/crypto/tests --target NativeBench    --plain
```

"Pure" forces `BESKID_CRYPTO_PROVIDER=pure`; "Native" is the OpenSSL 3 provider of ruling R27.
"Before" is commit dfc0772 (R27 provider, no hot-path changes); "after" is this branch.

## Results

| Benchmark | Mode | Before (dfc0772) | After |
| --- | --- | --- | --- |
| TLS 1.3 full handshake, loopback (best of 3) | AES-128-GCM pure / native | 228 / 252 ms | 4.05 / 4.17 ms |
| TLS 1.3 full handshake | ChaCha20-Poly1305 pure / native | 252 / 252 ms | 4.50 / 4.55 ms |
| TLS 8 MiB in 16 KiB records over TlsStream (seal+open, one core) | AES-128-GCM pure / native | 33 / 48 MB/s | 18.2 / 20.9 MB/s (note) |
| same | ChaCha20-Poly1305 pure / native | 43 / 46 MB/s | 20.0 / 21.5 MB/s (note) |
| TLS `Record.Seal` / `Open` 16 KiB, in memory | AES-128-GCM pure | 191 / 192 MB/s | pending (TlsMicroBench) |
| same | AES-128-GCM native | 1350 / 1411 MB/s | pending |
| same | ChaCha20-Poly1305 pure / native | 511-522 / 1135-1180 MB/s | pending |
| `Slice.New(16384)` vs 4 KiB literal | - | 98-155 ms | 35 us (4 KiB) |
| h2c GETs over loopback TCP | 512 x 16 KiB | 0.047 MB/s (176.5 s) | pending (Http2Bench) |
| h2 DATA frame decode / encode 16 KiB, in memory | - | 106 / 128 ms per frame | pending |
| HPACK encode / decode, 6-field request, Huffman | - | 283 / 14.4 us | pending |
| HPACK Huffman decode, 48 octets | - | 27.8 us | pending |
| QUIC handshake + 2 MiB stream in 4 KiB writes | pure, native | not finished in 60 min | pending (QuicBench) |

Note: the before and after transfer runs had different builder load (17 vs 5-7), and after
the change the first 16 KiB record grows each 4 KiB record buffer once (about 120 ms per
buffer, PERF1) inside the 0.4 s timed window. The in-memory record layer runs at
191-1411 MB/s, so the loopback transfer is bound by that one-time growth and the runtime
TCP path (two reads per record, fiber wake-ups), not by the AEAD. Pending rows come from
the acceptance chains still running on the builder (`/workspace/net-crypto-select-logs/`).

## Same-machine references

From `packages/crypto/BENCHMARKS.md` (`openssl speed -seconds 2`, OpenSSL 3.0.20, best of 3):
AES-128-GCM 16 KiB 6387 MB/s (no AES-NI: 467 MB/s), ChaCha20-Poly1305 5032 MB/s, X25519
21.7 us, ECDSA P-256 sign 13.2 us and verify 40.3 us. `openssl s_time` and Go (`crypto/tls`,
`quic-go`) or Rust (`rustls`, `quinn`) loopback equivalents were not measured on this host:
not measured.

## Where the time goes

- Handshake: about 200 ms of the 228 ms was `Slice.New` of the two 16.6 KiB record buffers
  (COMPILER-GAPS PERF1). Buffers start as 4 KiB literals and grow once; the handshake is now
  4 ms, dominated by the pure X25519, ECDSA and X.509 code.
- HTTP/2: each DATA frame decode and each body allocation was a quadratic `Slice.New`; HPACK
  encode converted names to bytes for each comparison. Now memmove copies, the first DATA
  payload is adopted as the body, name comparison does not allocate, and Huffman decoding
  is a 4-bit automaton stored in a string literal (an array literal of 4096 entries cost
  about 2 minutes of CLIF generation per test).
- QUIC: header protection is two CLIF blocks (first-byte mask, 32-bit masked XOR of the
  packet number); packet number decoding is constant-time arithmetic; ACK range sets hold at
  most 32 pairs and did not show up.
- Moved to CLIF: `Codec.Mem.Copy`/`Zero` (libc memmove/memset on payloads), QUIC
  `MaskFirst`/`MaskPn`, WebSocket `Xor64`, and the OpenSSL EVP calls of `Crypto.Native` (R27).
- Remaining limit: buffers above 4 KiB still allocate in O(n^2) and a larger literal costs
  minutes of compile time (PERF1); a sized allocation primitive in the compiler removes it.

## Sized allocation, geometric growth and heap reuse (0.5.3 CLI, kit4, 2026-10-07)

Same targets, one run each, builder load 4-6. "Before" is the kit3 acceptance run of
2026-10-06/07 (`/workspace/net-crypto-select-logs/accA2-*`, `accB-quic-QuicBench.log`);
"after" adds `Array.Zeroed`/`Slice.New` as one allocation, geometric `Array.Append`, and span
reuse across page counts and regions (COMPILER-GAPS ALLOC1). No package code changed.

| Benchmark | Mode | Before (kit3) | After (kit4) |
| --- | --- | --- | --- |
| `Slice.New(16384)` | - | 90539 us | 10 us |
| TLS 1.3 full handshake, loopback (best) | AES-128-GCM pure / native | 3.78 / 3.74 ms | 2.72 / 2.57 ms |
| same | ChaCha20-Poly1305 pure / native | 4.05 / 4.12 ms | 2.85 / 3.11 ms |
| TLS 8 MiB in 16 KiB records over TlsStream | AES-128-GCM pure / native | 19.96 / 23.60 MB/s | 71.80 / 192.26 MB/s |
| same | ChaCha20-Poly1305 pure / native | 22.94 / 23.27 MB/s | 130.97 / 182.75 MB/s |
| TLS `Record.Seal` / `Open` 16 KiB | AES-128-GCM pure | 210 / 213 MB/s | 214 / 213 MB/s |
| same | AES-128-GCM native | 2466 / 2515 MB/s | 2400 / 2574 MB/s |
| same | ChaCha20-Poly1305 pure / native | 636-646 / 1821-1922 MB/s | 662-664 / 1967-2001 MB/s |
| plain TCP 8 MiB in 16 KiB writes | - | 366.5 MB/s | 351.5 MB/s |
| h2c GETs over loopback TCP | 2048 x 4 KiB | 0.08 MB/s | 0.08 MB/s |
| same | 64 x 16 KiB | 0.12 MB/s | 0.25 MB/s |
| h2 DATA frame decode / encode 4 KiB, in memory | - | 513.5 / 0.68 MB/s | 446.4 / 1204.5 MB/s |
| HPACK encode / decode, 6-field request | - | 142.2 / 11.6 us | 140.8 / 10.8 us |
| HPACK Huffman decode, 48 octets | - | 50.2 us | 53.2 us |
| QUIC handshake (best) | AES-128-GCM pure / native | 1243 ms / - | 9.4 / 9.8 ms |
| QUIC 2 MiB stream in 4 KiB writes | AES-128-GCM pure / native | 0.22 MB/s / - | 2.60 / 2.70 MB/s |

The TLS transfer gains come from the record buffers: growing a 4 KiB buffer to 16 KiB no
longer costs about 100 ms. The in-memory AEAD, HPACK and plain TCP rows do not allocate in
their timed loops and are unchanged within noise. h2c GETs stay bound by the per-request
fiber and frame round trips, not by allocation. QUIC gains come from the 8 KiB scratch and
stream buffers; "before" had only a pure-provider row.
