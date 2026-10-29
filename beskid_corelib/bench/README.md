# Corelib benchmarks

Throughput and latency benchmarks of the crypto, TLS, QUIC and HTTP/2 packages. Each `test`
item prints `BENCH` lines and checks only that the measured operation succeeded. This project
is not part of the test matrix: run a target on purpose, on a quiet machine.

```bash
beskid test --project beskid_corelib/bench --target CryptoBench --plain
```

Results are in `packages/crypto/BENCHMARKS.md` and `docs/networking/BENCHMARKS.md`.
