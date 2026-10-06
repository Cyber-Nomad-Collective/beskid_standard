#!/bin/bash
# Web facade interop (not a Beskid test). Builds the release interop binary, then
#  1. curl --http2 / --http1.1 over TLS and curl over plain HTTP / h2c against the
#     Beskid server (Web.ServeTls on 18443, Web.ServePlain on 18080);
#  2. the Beskid client (Web.Exchange) against a Node.js TLS server that offers
#     h2 and http/1.1 (18444).
# OpenSSL s_server -www answers HTTP/1.0 with a close-delimited body, which the
# corelib HTTP/1.1 codec rejects by design, so Node.js is the client peer.
# Usage: protocols/web/interop/curl-interop.sh
set -u
here="$(cd "$(dirname "$0")" && pwd)"
certs="$here/../../tls/tests/interop/certs"
export BESKID_RUNTIME_PREFIX="${BESKID_RUNTIME_PREFIX:-/Users/mikserek/Projects/beskid/.worktrees/net-kit-0.5.2}"
unset BESKID_CORELIB_ROOT
log="${WEB_INTEROP_LOG:-$(mktemp -d)}"
bin="$here/obj/web-interop"
mkdir -p "$here/obj"
fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: expected [$2] got [$3]"; fail=1; fi
}
if [ ! -x "$bin" ] || [ -n "${WEB_INTEROP_REBUILD:-}" ]; then
  beskid build --project "$here/web_interop.bproj" --target WebInterop --release --output "$bin" --plain >"$log/build.log" 2>&1 \
    || { echo "FAIL: build"; grep -v INFO "$log/build.log" | tail -20; exit 1; }
fi

# 1. curl -> Beskid server
WEB_INTEROP_MODE=server WEB_INTEROP_TLS_CONNECTIONS=4 WEB_INTEROP_PLAIN_CONNECTIONS=2 "$bin" >"$log/server.log" 2>&1 &
pid=$!
for _ in $(seq 1 60); do grep -q '^ready' "$log/server.log" && break; sleep 1; done
grep -q '^ready' "$log/server.log" || { echo "FAIL: server did not start"; tail -20 "$log/server.log"; kill $pid 2>/dev/null; exit 1; }
tls=https://localhost:18443
c() { curl -s --max-time 30 --cacert "$certs/ca.pem" -w ' %{http_version} %{http_code}' "$@"; }
check "curl --http2 GET" "hello /hello?a=1 2 200" "$(c --http2 "$tls/hello?a=1")"
head -c 3000 /dev/zero > "$log/body"
check "curl --http2 POST 3000" "received 3000 2 200" "$(c --http2 --data-binary @"$log/body" "$tls/upload")"
check "curl --http1.1 GET" "hello /one 1.1 200" "$(c --http1.1 "$tls/one")"
check "curl --http1.1 keep-alive, two requests" "hello /a 1.1 200hello /b 1.1 200" "$(c --http1.1 "$tls/a" "$tls/b")"
check "curl plain http/1.1" "hello /plain 1.1 200" "$(c --http1.1 "http://127.0.0.1:18080/plain")"
check "curl h2c prior knowledge" "hello /h2c 2 200" "$(c --http2-prior-knowledge "http://127.0.0.1:18080/h2c")"
wait $pid
echo "--- server log"; grep -v '^|\|INFO' "$log/server.log" | tail -5

# 2. Beskid client -> Node.js (h2 + http/1.1)
if command -v node >/dev/null; then
  node "$here/node-server.js" "$certs" 18444 >"$log/node.log" 2>&1 &
  npid=$!
  for _ in $(seq 1 20); do grep -q '^ready' "$log/node.log" && break; sleep 0.5; done
  client() { WEB_INTEROP_MODE=client WEB_INTEROP_URL="$1" WEB_INTEROP_ALPN="$2" WEB_INTEROP_METHOD="${3:-GET}" WEB_INTEROP_BODY_BYTES="${4:-0}" "$bin" 2>&1 | grep -v '^|\|INFO' | tail -1; }
  check "Beskid client h2 GET -> node" "h2 200 node 2.0 /x?y=1" "$(client "https://localhost:18444/x?y=1" "h2,http/1.1")"
  check "Beskid client h2 POST -> node" "h2 200 node received 5000" "$(client "https://localhost:18444/p" "h2,http/1.1" POST 5000)"
  check "Beskid client http/1.1 GET -> node" "http/1.1 200 node 1.1 /one" "$(client "https://localhost:18444/one" "http/1.1")"
  check "Beskid client http/1.1 POST -> node" "http/1.1 200 node received 5000" "$(client "https://localhost:18444/p" "http/1.1" POST 5000)"
  kill $npid 2>/dev/null; wait $npid 2>/dev/null
else
  echo "SKIP: node not found (Beskid client interop)"
fi
[ -z "${WEB_INTEROP_LOG:-}" ] && rm -rf "$log"
exit $fail
