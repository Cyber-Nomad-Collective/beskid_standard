"""Pack and publish beskid_corelib package to pckg."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


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


def _parse_pack_resolved_version(output: str) -> str:
    prefix = "Resolved package version: "
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise SystemExit(
        "Could not parse resolved version from `beskid pckg pack` output; "
        f"expected a line starting with {prefix!r}.\nOutput:\n{output}"
    )


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

    cli_bin = _ensure_cli()
    # Fixed path: pack resolves semver internally (patch bump over package.json baseline
    # and/or .beskid/pckg-version-state.json); do not pass --version so we match that.
    artifact = ROOT / "beskid_corelib-pack.bpk"
    if artifact.exists():
        artifact.unlink()

    common = [str(cli_bin), "pckg", "--base-url", base_url]
    pack_env = {
        **os.environ,
        "BESKID_CORELIB_ROOT": str(ROOT / ".ci-cache" / "beskid_corelib"),
    }
    pack_result = subprocess.run(
        common
        + [
            "pack",
            "--package",
            "beskid_corelib",
            "--source",
            str(CORELIB_SOURCE),
            "--output",
            str(artifact),
        ],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=pack_env,
    )
    combined_out = (pack_result.stdout or "") + (pack_result.stderr or "")
    resolved_version = _parse_pack_resolved_version(combined_out)
    if project_version != resolved_version:
        print(
            f"[publish] Project.proj version={project_version!r}; "
            f"pckg resolved pack/upload version {resolved_version!r}."
        )
    subprocess.run(
        common
        + [
            "upload",
            "beskid_corelib",
            "--version",
            resolved_version,
            "--artifact",
            str(artifact),
        ],
        check=True,
        cwd=ROOT,
    )
    print(f"Published beskid_corelib {resolved_version} to {base_url}")

    if os.environ.get("CI_KEEP_ARTIFACT", "").strip().lower() not in {"1", "true", "yes"}:
        artifact.unlink(missing_ok=True)
    if os.environ.get("CI_KEEP_TOOLS", "").strip().lower() not in {"1", "true", "yes"}:
        shutil.rmtree(ROOT / ".ci-tools", ignore_errors=True)


if __name__ == "__main__":
    main()
