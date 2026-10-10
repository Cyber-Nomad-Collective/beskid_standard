# Connect

`corelib_connect` opens TCP connections with Happy Eyeballs version 2 (RFC 8305).
It uses `Network.Dns`, `Network.Tcp.TcpStream`, and Concurrency fibers.

## API

- `Connect.ConnectHost(hostName, port, policy)` resolves the name, orders the
  addresses (RFC 8305 section 4), and races staggered attempts. The first
  connected stream wins. All other attempts are cancelled, closed, and joined
  before the call returns.
- `Connect.ConnectAddresses(addresses, port, policy)` races caller-resolved addresses.
- `Connect.Policy.ConnectPolicy` sets the attempt delay, the family filter, and
  the total timeout. `Connect.Failures.ConnectError` reports each failed attempt.

## Limits

- The attempt delay is 250 ms, clamped to 100 ms through 2 s. The resolution
  delay is 50 ms. IPv6 goes first (ruling R3).
- A call starts at most 64 attempts.
- Set `ConnectPolicy.timeout` when the calling fiber can be cancelled. A
  cancelled fiber does not run cleanup (COMPILER-GAPS C11).
