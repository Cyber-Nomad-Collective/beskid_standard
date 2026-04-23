"""Pack and publish beskid_corelib package to pckg."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from ci.version import resolve_version


ROOT = Path(__file__).resolve().parents[1]
CORELIB_SOURCE = ROOT / "beskid_corelib"
CLI_DOWNLOAD_URL = (
    "https://github.com/Cyber-Nomad-Collective/beskid_compiler/releases/download/"
    "cli-latest/beskid-linux-amd64"
)


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def _project_field(content: str, key: str) -> str | None:
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip('"')
    return None


def _corelib_version(content: str) -> str:
    version = _project_field(content, "version")
    if not version:
        raise SystemExit("Project.proj is missing version")
    return version


def _ensure_cli() -> Path:
    override = os.environ.get("BESKID_CLI_BIN", "").strip()
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            raise SystemExit(f"BESKID_CLI_BIN does not exist: {path}")
        return path

    out = ROOT / ".ci-tools" / "beskid"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.is_file():
        subprocess.run(["curl", "-fsSL", CLI_DOWNLOAD_URL, "-o", str(out)], check=True, cwd=ROOT)
        out.chmod(0o755)
    return out


def main() -> None:
    _require("BESKID_PCKG_API_KEY")
    release_version = os.environ.get("RELEASE_VERSION", "").strip() or resolve_version()
    base_url = os.environ.get("BESKID_PCKG_BASE_URL", "https://pckg.beskid-lang.org").strip()

    manifest = CORELIB_SOURCE / "Project.proj"
    if not manifest.is_file():
        raise SystemExit(f"Project.proj not found: {manifest}")

    manifest_content = manifest.read_text(encoding="utf-8")
    project_name = _project_field(manifest_content, "name")
    if project_name != "beskid_corelib":
        raise SystemExit(
            f"Project.proj name must be 'beskid_corelib' for publishing, got {project_name!r}"
        )

    project_version = _corelib_version(manifest_content)
    if project_version != release_version:
        print(
            f"[publish] version mismatch detected: Project.proj={project_version}, "
            f"release={release_version}; publishing release version."
        )

    cli_bin = _ensure_cli()
    artifact = ROOT / f"beskid_corelib-{release_version}.bpk"
    if artifact.exists():
        artifact.unlink()

    common = [str(cli_bin), "pckg", "--base-url", base_url]
    subprocess.run(
        common
        + [
            "pack",
            "--package",
            "beskid_corelib",
            "--version",
            release_version,
            "--source",
            str(CORELIB_SOURCE),
            "--output",
            str(artifact),
        ],
        check=True,
        cwd=ROOT,
        env={
            **os.environ,
            "BESKID_CORELIB_ROOT": str(ROOT / ".ci-cache" / "beskid_corelib"),
        },
    )
    subprocess.run(
        common
        + [
            "upload",
            "beskid_corelib",
            "--version",
            release_version,
            "--artifact",
            str(artifact),
        ],
        check=True,
        cwd=ROOT,
    )
    print(f"Published beskid_corelib {release_version} to {base_url}")

    if os.environ.get("CI_KEEP_ARTIFACT", "").strip().lower() not in {"1", "true", "yes"}:
        artifact.unlink(missing_ok=True)
    if os.environ.get("CI_KEEP_TOOLS", "").strip().lower() not in {"1", "true", "yes"}:
        shutil.rmtree(ROOT / ".ci-tools", ignore_errors=True)


if __name__ == "__main__":
    main()
