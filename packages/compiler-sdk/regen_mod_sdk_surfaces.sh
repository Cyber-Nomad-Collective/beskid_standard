#!/usr/bin/env bash
# Regenerate the generator-owned surfaces: syntax nodes, the query facade and the
# diagnostics mirror (`SemanticIssueKind`, `Severity`). Compiler contract, request,
# semantic and workspace sources are maintained as source. The beskid_ast_reflect_gen
# `sdk_surfaces` tests fail while any generated surface here is stale.
set -euo pipefail

COMPILER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$COMPILER_ROOT"
SDK_BESKID_DIR="corelib/packages/compiler-sdk/src/Beskid"
SDK_QUERY="$SDK_BESKID_DIR/Compiler/Query.bd"
QUERY_STAGE="$(mktemp "${SDK_QUERY}.staged.XXXXXX")"
trap 'rm -f "$QUERY_STAGE"' EXIT

cargo run --locked -p beskid_ast_reflect_gen --quiet -- \
  --quiet --workspace "$COMPILER_ROOT" --emit-syntax-sdk "$SDK_BESKID_DIR"
cargo run --locked -p beskid_ast_reflect_gen --quiet -- \
  --quiet --workspace "$COMPILER_ROOT" --emit-query-facade >"$QUERY_STAGE"
# Publish only a complete successful query generation; a failed command cannot
# truncate the checked-in callback facade.
mv "$QUERY_STAGE" "$SDK_QUERY"
trap - EXIT
cargo run --locked -p beskid_ast_reflect_gen --quiet -- \
  --workspace "$COMPILER_ROOT" --emit-diagnostics-sdk "$SDK_BESKID_DIR/Compiler/Diagnostics.bd"
printf 'Regenerated syntax, query and diagnostics surfaces under %s/%s\n' "$COMPILER_ROOT" "$SDK_BESKID_DIR"
