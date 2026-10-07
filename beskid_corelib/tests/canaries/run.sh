#!/usr/bin/env bash
# Runs every compiler-gap canary and reports which still reproduce.
# Usage: run.sh [path-to-beskid]   (defaults to `beskid` on PATH)
# Run from a Corelib tree the compiler trusts (an installed bundle, or a copy with a recomputed
# .beskid-bundle.sha256 marker); see docs/Authoring-Limits-0.5.2.md.
set -u
BESKID="${1:-beskid}"
cd "$(dirname "$0")"
fixed=0
open=0
while IFS=$'\t' read -r target description; do
  rm -f Project.lock
  result=$(timeout 180 "$BESKID" test --project . --target "$target" --plain </dev/null 2>&1 | grep -E "^Result:" | tail -1)
  if [[ "$result" == *"failed=0"* && "$result" != *"passed=0"* ]]; then
    echo "FIXED       $target  $description"
    fixed=$((fixed + 1))
  else
    echo "REPRODUCES  $target  $description"
    open=$((open + 1))
  fi
done < targets.txt
echo "fixed=$fixed reproduces=$open"
