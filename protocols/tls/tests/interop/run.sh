#!/bin/bash
# Interop between the Beskid TLS 1.3 implementation and OpenSSL 3 (s_server / s_client).
# Usage: protocols/tls/tests/interop/run.sh [quick]
# Requires: beskid 0.5.2 with BESKID_RUNTIME_PREFIX set (see protocols/PLAN.md), OpenSSL 3.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CERTS="$HERE/certs"
PROJECT="$HERE/project"
OPENSSL="${OPENSSL:-/opt/homebrew/bin/openssl}"
LOG="${TLS_INTEROP_LOG:-$(mktemp -d)}"
export BESKID_RUNTIME_PREFIX="${BESKID_RUNTIME_PREFIX:-/Users/mikserek/Projects/beskid/.worktrees/net-kit-0.5.2}"
unset BESKID_CORELIB_ROOT
export RUST_LOG=error
PASS=0; FAIL=0
report() { if [ "$2" = 0 ]; then echo "PASS $1"; PASS=$((PASS+1)); else echo "FAIL $1 ($3)"; FAIL=$((FAIL+1)); fi; }
wait_file() { # path pid: the Beskid server writes the file after binding its listener
  for _ in $(seq 1 900); do
    [ -f "$1" ] && return 0
    kill -0 "$2" 2>/dev/null || return 1
    sleep 1
  done; return 1; }
wait_port() { # port [pid]
  for _ in $(seq 1 900); do
    nc -z 127.0.0.1 "$1" 2>/dev/null && return 0
    if [ -n "${2:-}" ] && ! kill -0 "$2" 2>/dev/null; then return 1; fi
    sleep 1
  done; return 1; }

# Beskid client -> openssl s_server -www
client_case() { # name suite(hex code decimal) group(decimal) opensslSuite opensslGroup [alpn]
  local name=$1 suite=$2 group=$3 osuite=$4 ogroup=$5 alpn=${6:-} port=$((44400 + RANDOM % 500))
  local extra=(); [ -n "$alpn" ] && extra=(-alpn "$alpn")
  "$OPENSSL" s_server -accept "$port" -cert "$CERTS/server.pem" -key "$CERTS/server.key" -tls1_3 \
     -ciphersuites "$osuite" -groups "$ogroup" -www -naccept 1 ${extra[@]+"${extra[@]}"} > "$LOG/$name.server.log" 2>&1 &
  local spid=$!
  sleep 1
  TLS_INTEROP_PORT=$port TLS_INTEROP_SUITE=$suite TLS_INTEROP_GROUP=$group TLS_INTEROP_ALPN=$alpn TLS_INTEROP_TIMING="$LOG/$name.ms" \
    beskid test --project "$PROJECT" --target InteropClient --plain --target-timeout 900 > "$LOG/$name.beskid.log" 2>&1
  local rc=$?
  grep -q "passed=1" "$LOG/$name.beskid.log" || rc=1
  kill $spid 2>/dev/null; wait $spid 2>/dev/null
  [ -f "$LOG/$name.ms" ] && echo "     handshake $(cat "$LOG/$name.ms") ms"
  report "$name" $rc "$LOG/$name.beskid.log"
}

# openssl s_client -> Beskid server
server_case() { # name group(decimal) opensslSuite opensslGroups [alpn]
  local name=$1 group=$2 osuite=$3 ogroups=$4 alpn=${5:-} port=$((44900 + RANDOM % 500))
  rm -f "$LOG/$name.ready"
  TLS_INTEROP_PORT=$port TLS_INTEROP_GROUP=$group TLS_INTEROP_ALPN=$alpn TLS_INTEROP_READY="$LOG/$name.ready" \
    beskid test --project "$PROJECT" --target InteropServer --plain --target-timeout 900 > "$LOG/$name.beskid.log" 2>&1 &
  local bpid=$!
  if ! wait_file "$LOG/$name.ready" $bpid; then kill $bpid 2>/dev/null; report "$name" 1 "server did not listen"; return; fi
  local extra=(); [ -n "$alpn" ] && extra=(-alpn "$alpn")
  printf 'hello beskid\n' | "$OPENSSL" s_client -connect 127.0.0.1:$port -servername localhost -tls1_3 \
     -ciphersuites "$osuite" -groups "$ogroups" -CAfile "$CERTS/ca.pem" -verify_return_error -verify_hostname localhost \
     -ign_eof ${extra[@]+"${extra[@]}"} > "$LOG/$name.client.log" 2>&1
  local rc=$?
  wait $bpid; local brc=$?
  grep -q "passed=1" "$LOG/$name.beskid.log" || brc=1
  grep -q "hello beskid" "$LOG/$name.client.log" || rc=1
  grep -q "Verify return code: 0" "$LOG/$name.client.log" || rc=1
  [ $brc = 0 ] || rc=1
  report "$name" $rc "$LOG/$name.client.log"
}

client_case client-aes128-x25519 4865 29 TLS_AES_128_GCM_SHA256 X25519
client_case client-chacha-p256 4867 23 TLS_CHACHA20_POLY1305_SHA256 P-256
if [ "${1:-}" != quick ]; then
  client_case client-aes256-x25519-alpn 4866 29 TLS_AES_256_GCM_SHA384 X25519 h2
fi
server_case server-aes128-x25519 29 TLS_AES_128_GCM_SHA256 X25519
if [ "${1:-}" != quick ]; then
  server_case server-chacha-hrr-p256 23 TLS_CHACHA20_POLY1305_SHA256 X25519:P-256
  server_case server-aes256-alpn 29 TLS_AES_256_GCM_SHA384 X25519 http/1.1
fi
echo "interop: $PASS passed, $FAIL failed (logs in $LOG)"
[ $FAIL = 0 ]
