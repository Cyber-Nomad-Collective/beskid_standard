# Networking program rulings

Decisions made without the owner present, with the basis for each. Revisit any
of them through an OpenSpec change when this work is specified.

| # | Date | Ruling | Basis |
| --- | --- | --- | --- |
| R1 | 2026-10-05 | Protocol packages live in `protocols/` and depend on an unmodified 0.5.2 corelib until a CLI grants corelib authority per service file (0.5.3). Then they move to `corelib/packages/`. | 0.5.2 grants corelib services only to a byte-identical bundle (`beskid_abi/src/corelib_bundle.rs`). |
| R2 | 2026-10-05 | Coordination inside a connection uses preallocated flag arrays, `Fiber.Join` and short polls, never one channel per connection or stream. | 0.5.2 runtime: 64 channels per process, never freed (COMPILER-GAPS C10). |
| R3 | 2026-10-05 | Happy Eyeballs: 250 ms connection attempt delay (clamped 100 ms..2 s), 50 ms resolution delay, IPv6 first, interleaved families. | RFC 8305 sections 3, 4, 5, 8. |
| R4 | 2026-10-05 | URI parsing rejects inet_aton host forms (`127.1`, `0x7f.1`, `2130706433`) and accepts only strict dotted-decimal IPv4. | RFC 3986 section 7.4 warns about rare IP address formats; WHATWG URL treats them differently, so strict rejection avoids ambiguity. |
| R5 | 2026-10-05 | AES and GHASH are table-based for now (not constant-time against cache timing); they move to hardware instructions through CLIF blocks in 0.5.3. | Performance and side-channel guidance: Bernstein 2005 cache-timing; Go/BoringSSL use AES-NI/PMULL. |
| R6 | 2026-10-05 | RSA keys in certificate validation require at least 2048 bits. | NIST SP 800-57 Part 1 Rev. 5 table 2; CA/Browser Forum Baseline Requirements 6.1.5. |
| R7 | 2026-10-05 | X.509 tolerates keyUsage BIT STRINGs with trailing zero bits and an explicit `critical FALSE`, because real roots in the macOS bundle encode them; negative serial numbers stay rejected. | RFC 5280 section 4.1.2.2 and 4.2; observed in `/etc/ssl/cert.pem`. |
| R8 | 2026-10-05 | WebSocket never offers extensions (no permessage-deflate) and caps messages at 64 KiB by default. | RFC 6455 section 9; RFC 7692 is optional; runtime array limit (W5). |
| R9 | 2026-10-05 | Messages larger than buffers are written in pieces (header, then payload through a 4 KiB scratch buffer); nothing buffers whole bodies. | Runtime traps out_of_memory near 160 KiB of live arrays (W5). |
| R10 | 2026-10-06 | AES is vector-permute AES (vpaes) and GHASH is BearSSL ghash_ctmul64, both constant time, replacing the table versions of R5; hardware AES/CLMUL waits for compiler opcodes. | Hamburg, CHES 2009; OpenSSL vpaes-x86_64.pl; BearSSL ghash_ctmul64.c; Cranelift 0.136 has no AES/CLMUL opcodes. |
| R11 | 2026-10-06 | Poly1305 uses radix 2^64 with 128-bit products (OpenSSL poly1305.c) instead of donna 5x26. | RFC 8439 2.5; 64x64 products available through `umulhi`. |
| R12 | 2026-10-06 | 256-bit fields (X25519, P-256, ECDSA mod n) use generic 4x64 Montgomery CIOS with masked final subtraction; X25519 keeps the RFC 7748 ladder with masked swaps. | Koc-Acar-Kaliski 1996; RFC 7748 5; Renes-Costello-Batina 2016 complete formulas unchanged. |
