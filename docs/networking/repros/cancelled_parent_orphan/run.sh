#!/usr/bin/env bash
# Runs every target of this repro with the active toolchain, one `beskid test` per target.
# Env: BESKID (default: beskid); BESKID_RUNTIME_PREFIX must point at a runtime kit.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
for target in Gap Workaround; do
  echo "=== target $target ==="
  ${BESKID:-beskid} test --project "$here" --target "$target" --plain 2>&1 | grep -v INFO
done
