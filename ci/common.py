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
_WORKSPACE_MANIFEST = ROOT / "CoreLib.bws"


def workspace_cli_candidates() -> list[Path]:
    """Prefer a locally built compiler workspace CLI when nested under `compiler/corelib`."""
    compiler_root = ROOT.parent
    if not (compiler_root / "Cargo.toml").is_file():
        return []
    return [
        compiler_root / "target" / "release" / "beskid_cli",
        compiler_root / "target" / "debug" / "beskid_cli",
    ]


def ensure_cli() -> Path:
    override = os.environ.get("BESKID_CLI_BIN", "").strip()
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if path.is_file():
            return path
        raise SystemExit(f"BESKID_CLI_BIN does not exist: {path}")

    for candidate in workspace_cli_candidates():
        if candidate.is_file():
            return candidate

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


def discover_project_manifest(project_dir: Path) -> Path:
    matches = sorted(project_dir.glob("*.bproj"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"No `.bproj` manifest found in {project_dir}")
    names = ", ".join(path.name for path in matches)
    raise SystemExit(f"Expected exactly one `.bproj` in {project_dir}, found: {names}")


def workspace_manifest_path() -> Path:
    return _WORKSPACE_MANIFEST


def parse_project_targets(manifest: Path) -> list[str]:
    text = manifest.read_text(encoding="utf-8")
    return _TARGET_PATTERN.findall(text)
