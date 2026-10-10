#!/bin/bash
# Optional interop check: Node's built-in WebSocket client (undici) against the
# Beskid echo server. Needs node >= 22 and the environment from docs/networking/PLAN.md.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
export BESKID_RUNTIME_PREFIX="${BESKID_RUNTIME_PREFIX:?set BESKID_RUNTIME_PREFIX to a beskid 0.5.3 runtime kit}"
BESKID="${BESKID:-beskid}"
unset BESKID_CORELIB_ROOT
log="$(mktemp)"
"$BESKID" test --project "$here" --target WsInteropServer --plain --target-timeout 900 >"$log" 2>&1 &
server=$!
node "$here/client.mjs" &
client=$!
# Stop the client if the server ends first (compile error, bind failure).
while kill -0 "$client" 2>/dev/null; do
  if ! kill -0 "$server" 2>/dev/null; then sleep 5; kill "$client" 2>/dev/null; break; fi
  sleep 1
done
wait "$client"; clientStatus=$?
wait "$server"; serverStatus=$?
grep -E '^(PASS|FAIL)|Result:|×' "$log"
rm -f "$log"
if [ "$clientStatus" -ne 0 ] || [ "$serverStatus" -ne 0 ]; then echo "interop: FAILED"; exit 1; fi
echo "interop: OK"
