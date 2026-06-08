#!/usr/bin/env bash
# Regenerate checked-in combinator parsers from package-local .pest grammars.
set -euo pipefail

COMPILER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FOUNDATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRAMMAR="$FOUNDATION_DIR/grammars/regex.pest"
OUTPUT="$FOUNDATION_DIR/src/Core/Text/Regex/Generated.bd"

cd "$COMPILER_ROOT"
cargo run -q -p beskid_pest_gen --bin emit_grammar -- \
  "$GRAMMAR" \
  "$OUTPUT" \
  regex
