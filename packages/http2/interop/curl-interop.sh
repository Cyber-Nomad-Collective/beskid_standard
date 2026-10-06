#!/bin/bash
# Optional HTTP/2 interop check (not a Beskid test): builds the Beskid h2c
# server (release AOT; `beskid run` needs a debug runtime kit the local kit
# lacks), starts it and talks to it with curl --http2-prior-knowledge.
# Usage: protocols/http2/interop/curl-interop.sh
set -u
here="$(cd "$(dirname "$0")" && pwd)"
export BESKID_RUNTIME_PREFIX="${BESKID_RUNTIME_PREFIX:-/Users/mikserek/Projects/beskid/.worktrees/net-kit-0.5.2}"
unset BESKID_CORELIB_ROOT
curl --version | grep -q HTTP2 || { echo "SKIP: curl lacks HTTP2"; exit 0; }
log="$(mktemp)"
bin="$here/obj/http2-interop-server"
mkdir -p "$here/obj"
beskid build --project "$here/http2_interop.bproj" --target Http2InteropServer --release --output "$bin" --plain >"$log" 2>&1 \
  || { echo "FAIL: build"; grep -v INFO "$log" | tail -20; exit 1; }
"$bin" >"$log" 2>&1 &
pid=$!
for _ in $(seq 1 600); do grep -q '^ready' "$log" && break; sleep 1; done
grep -q '^ready' "$log" || { echo "FAIL: server did not start"; tail -20 "$log"; kill $pid 2>/dev/null; exit 1; }
fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: expected [$2] got [$3]"; fail=1; fi
}
url=http://127.0.0.1:18089
get=$(curl -s --max-time 20 --http2-prior-knowledge -w ' %{http_version} %{http_code}' "$url/hello?a=1")
check "GET" "hello /hello?a=1 2 200" "$get"
head -c 100000 /dev/zero > "$log.body"
post=$(curl -s --max-time 30 --http2-prior-knowledge -w ' %{http_version} %{http_code}' --data-binary @"$log.body" "$url/upload")
check "POST 100000 bytes" "received 100000 2 200" "$post"
multi=$(curl -s --max-time 20 --http2-prior-knowledge "$url/a" "$url/b")
check "two requests, one connection" "hello /ahello /b" "$multi"
wait $pid
echo "--- server log"; grep -v '^|\|INFO' "$log" | tail -5
rm -f "$log" "$log.body"
exit $fail
