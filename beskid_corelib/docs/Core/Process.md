`Core.Process` provides typed child sessions through the canonical runtime. It
passes the executable and each argument separately; it does not evaluate a shell
command. `Id`, `Exit`, `CurrentId` and `IsCurrentProcess` remain available.

`Spawn(ProcessStartInfo)` returns `Result<ChildProcess, ProcessError>` and uses
a checked five-second setup settlement deadline. `SpawnUntil(info, deadline)`
uses the supplied absolute deadline. POSIX exec confirmation is nonblocking and
cooperative; timeout or cancellation closes and reaps a partially started child.
Synchronous OS process creation itself is a nonpreemptible native boundary: its
deadline is checked before and after settlement.
`ProcessStartInfo` supplies an executable path, arguments, working directory and
an explicit environment policy: `Inherit`, `Replace(entries)` or
`Extend(entries)`. Environment entries contain separate key and value strings.
Invalid UTF-8, interior NULs, duplicate override keys and invalid environment
keys fail before child execution. Windows environment keys follow the platform's
case-insensitive rule. Inherited POSIX entries are copied under the same lock as
canonical environment mutation, bounded to 1 MiB and 65,536 entries; native
borrowed environment pointers never survive that lock.

A child exposes `Stdin()` as a `ProcessWriter` and `Stdout()` and `Stderr()` as
`ProcessReader` values. They implement the existing `Core.IO.Writer`, `Reader`
and `Closer` contracts. Reads and writes are partial binary transfers: an empty
valid transfer succeeds without native work; a nonempty read returning zero is
EOF. Drain stderr separately while consuming stdout to avoid pipe backpressure.

`StdinUntil`, `StdoutUntil` and `StderrUntil` use one checked monotonic `Deadline`
for every retry. `TryRead` and `TryWrite` return `Result<Option<i64>, IoError>`;
`None` means readiness is pending. A pending write must be retried with its same
source prefix. A competing prefix returns Busy without replacing that write.
Framing pumps can call `WaitReady(deadline)` between probes, using the existing
cooperative wait and cancellation machinery.

`Wait(deadline)` returns a typed `ProcessExit`. Deadline expiry and cancellation
are distinct failures. `Terminate()` requests contained process-tree termination.
`Close()` invalidates the session, closes pipes, terminates when needed and reaps
the child under one five-second cleanup bound. Child and pipe values implement
`Disposable`; repeated close through aliases is idempotent. These values have
private source-issued capabilities and cannot be constructed from native tokens.

`Run(executable, arguments)` uses the same child authority to capture stdout and
stderr concurrently. It closes stdin, inherits the environment and returns
`ProcessOutput { exitCode, stdout, stderr }` for zero exit. Nonzero exit returns
`ProcessError::ExitCode(code, stderr)`. Capture admits at most 16 MiB combined
output and returns typed `IOError` for invalid UTF-8 or budget exhaustion. Use
the streaming interfaces for binary data and larger output.
