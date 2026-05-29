#!/usr/bin/env bash
# Install the rolling Beskid CLI from GitHub releases (same script as the docs site).
set -euo pipefail

INSTALL_SCRIPT_URL="${BESKID_CLI_INSTALL_SCRIPT_URL:-https://beskid-lang.org/install.sh}"

curl -fsSL "${INSTALL_SCRIPT_URL}" | bash
