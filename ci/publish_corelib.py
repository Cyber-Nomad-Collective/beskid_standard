"""Pack and publish beskid_corelib package to pckg."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
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


def _upsert_corelib_package(base_url: str, api_key: str) -> None:
    """Ensure the beskid_corelib package exists for this API key (POST /api/packages upsert)."""
    root = base_url.rstrip("/") + "/"
    url = urllib.parse.urljoin(root, "api/packages")
    payload = {
        "name": "beskid_corelib",
        "description": "Beskid standard library (corelib) distributed via pckg.",
        "category": "Library",
        "repositoryUrl": None,
        "websiteUrl": "https://beskid-lang.org",
        "tags": ["corelib", "standard-library"],
        "isPublic": True,
        "submitForReview": False,
        "reviewReason": None,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise SystemExit(
            f"Failed to upsert beskid_corelib metadata (HTTP {exc.code}): {detail or exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach pckg at {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        print(f"[publish] upsert: unexpected non-JSON response: {body[:500]!r}")
        return
    if not parsed.get("success", True):
        raise SystemExit(f"Upsert beskid_corelib failed: {parsed.get('message', body)}")
    print("[publish] ensured beskid_corelib package metadata (upsert ok)")


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
    api_key = _require("BESKID_PCKG_API_KEY")
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

    _upsert_corelib_package(base_url, api_key)

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
