# Network

`Network.Types`, `Network.Errors`, `Network.Dns`, `Network.Tcp`, and
`Network.Udp` provide portable Internet networking. The package depends only
on Foundation. Socket identity is private to the resource and runtime.

## Addresses and errors

`IpAddress::V4` contains four `u8` octets. `IpAddress::V6` contains four
network-order `u32` words, so both forms have an exact address width.
`SocketAddress` contains an `IpAddress` and a bounded `Port`.
`PortBytes(high, low)` constructs any 16-bit port without a narrowing cast;
`PortNumber(value)` checks a numeric input and returns `InvalidAddress` outside
0..65535. `Port.Value()` returns the numeric value. Port zero is accepted only
for binding, where it requests an OS-selected port.

`NetworkError` is a closed union with no native payload.
`ResourceExhausted` reports a full runtime socket table, a failed runtime or
native allocation, or host descriptor, buffer, or memory exhaustion; close
resources before retrying. `NetworkDown` is reserved for an unreachable
network, route, or host and for native failures that match no other variant.
The two variants are never substituted for one another. Its explicit
`CleanupConversion` maps `DisposeError::Failed` to `CleanupFailed` for scoped
cleanup; it is not a general implicit conversion. Socket options expose only
portable `noDelay` and `keepAlive` booleans.

## DNS

`Dns.Resolve(hostName, port, family)` takes an optional `AddressFamily`, starts
a fresh host resolver job, and returns all matching addresses in resolver
order. It adds no DNS cache. Cancellation ends the Beskid wait; it does not
promise to interrupt the native resolver. Foundation retains a separate active
work lease until the resolver actually exits, then discards a cancelled result.

## TCP

`TcpListener.Bind(address, backlog)` returns a listener, whose `Accept` returns
an owned `TcpStream`. `TcpStream.Connect(address, options)` creates a client.
Listeners expose `LocalAddress` and `Close`; streams additionally expose
`PeerAddress`, `SocketOptions`, `SetSocketOptions`, and `ShutdownWrite`.

`TcpStream` conforms to Foundation `Stream`, `Reader`, `Writer`, `Closer`, and
`Disposable`. Its `Read(destination, offset, count)`,
`Write(source, offset, count)`, and `Close()` use the existing `IoError`
signatures. Use `Core.IO.ReadExact` and `Core.IO.WriteAll` for transfer loops.
Successful zero-byte nonempty reads mean EOF; a write can complete partially.
`ShutdownWrite` preserves the read direction.

There is at most one accept per listener and one read plus one write per
stream. A competing operation creates no second wait. Lifecycle and option
admission return `NetworkError::Busy`; Stream admission or terminal failures
map to the relevant Foundation `ReadFailed(cause)` or `WriteFailed(cause)`
variant, keeping the Stream contract intact. The `TransferFailure` cause is
`Busy` for a competing same-direction operation, `Closed` for a local close,
stale handle, or unconnected stream, `Cancelled` and `TimedOut` when that wait
winner ends the operation, `PeerReset` for a peer abort, `PeerAborted` for a
connection aborted by the local stack, and `Unspecified` for every other
failure. An orderly peer close is not a failure: `Read` returns `Ok(0)`.

## UDP

`UdpSocket.Bind(address)` creates a datagram resource. `SendTo(payload, peer)`
and `ReceiveFrom(capacity)` preserve one datagram per operation. A received
`Datagram` contains its owned payload, source address, and truncation flag.
Zero-length payloads are datagrams, not EOF. `Connect(peer)` enables `Send`
and `Receive`; `LocalAddress` and `PeerAddress` remain typed.

One receive and one send may proceed concurrently. A competing same-direction
operation returns `Busy` without consuming its payload or installing a wait.
Sending borrows the caller's payload and leaves it owned by the caller. UDP
does not implement `Core.IO.Stream`.

## Lifetime and scheduling

All three resources implement Foundation `Disposable` and may be used in a
scoped `use` binding. Close invalidates the active generation, detaches pending
native work, posts owner-routed closed completions, and closes the socket once.
A repeated close cannot close a replacement socket in a reused table slot.
The handle remains opaque when the resource is transported through Foundation
channels; resource transport must preserve its sole ownership obligation.

Operations that may wait execute in a scheduler-owned fiber. Readiness,
cancellation, and close compete through Foundation's single terminal winner;
networking does not resume fibers itself. This API revision registers an
unbounded deadline (`-1`): Foundation does not yet expose a typed ambient
deadline context. No separate Network timer or transfer-settings API is added.

TLS, HTTP, Unix-domain sockets, raw sockets, multicast configuration, caching,
and native descriptor escape hatches are absent.

## Evidence

The existing corelib test project registers `NetworkTypesTests`,
`NetworkDnsTests`, `NetworkTcpTests`, `NetworkUdpTests`, and `NetworkScopeTests`. They cover bounded
ports, portable errors, DNS family filtering, independent resolver results,
TCP transfer through Core.IO, EOF, scoped cleanup, datagram truncation, empty
datagrams, connected UDP, and stale-generation behavior through public APIs.

`tests/compile-fail/RawHandle.bd` must reject private handle access;
`tests/compile-fail/UdpIsNotStream.bd` must reject using UDP as a stream. These
negative fixtures are outside the positive test source tree deliberately.
They have separate `RawHandle` and `UdpIsNotStream` targets in
`tests/compile-fail/network_rejections.bproj`.

Analyzer success alone is not execution evidence. Run the positive test targets
against a compiler and runtime kit built from the matching networking manifest.
