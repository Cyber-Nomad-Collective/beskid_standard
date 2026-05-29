"""Shared helpers for beskid_standard CI scripts."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_CLI_INSTALL_SCRIPT = ROOT / "ci" / "download_cli.sh"
_MANAGED_CLI_BIN = Path.home() / ".beskid" / "bin" / "beskid"
_TARGET_PATTERN = re.compile(r'^\s*target\s+"([^"]+)"\s*\{', re.MULTILINE)


def ensure_cli() -> Path:
    override = os.environ.get("BESKID_CLI_BIN", "").strip()
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if path.is_file():
            return path
        raise SystemExit(f"BESKID_CLI_BIN does not exist: {path}")

    if _MANAGED_CLI_BIN.is_file():
        return _MANAGED_CLI_BIN

    if not _CLI_INSTALL_SCRIPT.is_file():
        raise SystemExit(f"Missing CLI install script: {_CLI_INSTALL_SCRIPT}")

    subprocess.run(["bash", str(_CLI_INSTALL_SCRIPT)], check=True, cwd=ROOT)
    if not _MANAGED_CLI_BIN.is_file():
        raise SystemExit(
            f"CLI install script did not place a binary at {_MANAGED_CLI_BIN}. "
            "Set BESKID_CLI_BIN to an existing beskid executable."
        )
    return _MANAGED_CLI_BIN


def parse_project_targets(manifest: Path) -> list[str]:
    text = manifest.read_text(encoding="utf-8")
    return _TARGET_PATTERN.findall(text)
