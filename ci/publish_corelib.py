"""Pack and publish the Beskid corelib package (`corelib`) to pckg."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORELIB_SOURCE = ROOT / "beskid_corelib"
# Prebuilt Linux CLI (may lag source); prefer `BESKID_CLI_BIN` or CI-built binary.
_DEFAULT_CLI_DOWNLOAD_URL = (
    "https://github.com/Cyber-Nomad-Collective/beskid_compiler/releases/download/"
    "cli-latest/beskid-linux-amd64"
)
PACKAGE_ID = "corelib"


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


def _parse_pckg_published_version(output: str) -> str | None:
    prefix = "PCKG_PUBLISHED_VERSION="
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    # Human-readable summary line from beskid_pckg (same run as PCKG_PUBLISHED_VERSION=).
    m = re.search(
        r"(?m)^version:\s+(\S+)\s+\(registry-assigned\)\s*$",
        output,
    )
    if m:
        return m.group(1).strip()
    return None


def _default_icon_url(base_url: str) -> str:
    override = os.environ.get("BESKID_CORELIB_ICON_URL", "").strip()
    if override:
        return override
    root = base_url.rstrip("/") + "/"
    return urllib.parse.urljoin(root, "package-icons/corelib.svg")


def _upsert_corelib_package(base_url: str, api_key: str) -> None:
    """Ensure the corelib package exists for this API key (POST /api/packages upsert)."""
    root = base_url.rstrip("/") + "/"
    url = urllib.parse.urljoin(root, "api/packages")
    payload = {
        "name": PACKAGE_ID,
        "description": (
            "Beskid standard library: prelude, collections, filesystem helpers, and runtime "
            "contracts. Published from compiler/corelib/beskid_corelib."
        ),
        "category": "Library",
        "repositoryUrl": "https://github.com/Cyber-Nomad-Collective/beskid_compiler/tree/main/compiler/corelib/beskid_corelib",
        "websiteUrl": "https://beskid-lang.org",
        "tags": ["corelib", "stdlib", "beskid", "standard-library"],
        "isPublic": True,
        "submitForReview": False,
        "reviewReason": None,
        "iconUrl": _default_icon_url(base_url),
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
            f"Failed to upsert {PACKAGE_ID} metadata (HTTP {exc.code}): {detail or exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach pckg at {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        print(f"[publish] upsert: unexpected non-JSON response: {body[:500]!r}")
        return
    if not parsed.get("success", True):
        raise SystemExit(f"Upsert {PACKAGE_ID} failed: {parsed.get('message', body)}")
    print(f"[publish] ensured {PACKAGE_ID} package metadata (upsert ok)")


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
        url = os.environ.get("BESKID_CLI_DOWNLOAD_URL", "").strip() or _DEFAULT_CLI_DOWNLOAD_URL
        subprocess.run(["curl", "-fsSL", url, "-o", str(out)], check=True, cwd=ROOT)
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
    if project_name != PACKAGE_ID:
        raise SystemExit(
            f"Project.proj name must be {PACKAGE_ID!r} for publishing, got {project_name!r}"
        )

    _upsert_corelib_package(base_url, api_key)

    cli_bin = _ensure_cli()
    # Pack resolves semver for package.json inside the artifact; upload omits multipart
    # `version` so the registry assigns the next semver (see `PublishPackageVersionEndpoint`).
    artifact = ROOT / "corelib-pack.bpk"
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
            PACKAGE_ID,
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
    print((pack_result.stdout or "") + (pack_result.stderr or ""), end="")

    upload_cmd = common + [
        "upload",
        PACKAGE_ID,
        "--artifact",
        str(artifact),
    ]
    upload_result = subprocess.run(
        upload_cmd,
        check=False,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ},
    )
    upload_out = (upload_result.stdout or "") + (upload_result.stderr or "")
    if upload_result.returncode != 0:
        print(upload_out, end="", file=sys.stderr)
        raise SystemExit(
            f"`beskid pckg upload` failed (exit {upload_result.returncode}). "
            "Ensure the CLI supports upload without --version (registry-assigned semver); "
            "set BESKID_CLI_BIN to a current beskid build, or refresh cli-latest / "
            "BESKID_CLI_DOWNLOAD_URL."
        )
    published_version = _parse_pckg_published_version(upload_out)
    if not published_version:
        print(upload_out, end="", file=sys.stderr)
        raise SystemExit(
            "Upload succeeded but could not read the registry-assigned version from CLI output "
            "(expected PCKG_PUBLISHED_VERSION= or 'version: … (registry-assigned)')."
        )
    print(upload_result.stdout or "", end="")
    if upload_result.stderr:
        print(upload_result.stderr, end="", file=sys.stderr)
    print(f"Published {PACKAGE_ID} {published_version} to {base_url}")

    if os.environ.get("CI_KEEP_ARTIFACT", "").strip().lower() not in {"1", "true", "yes"}:
        artifact.unlink(missing_ok=True)
    if os.environ.get("CI_KEEP_TOOLS", "").strip().lower() not in {"1", "true", "yes"}:
        shutil.rmtree(ROOT / ".ci-tools", ignore_errors=True)


if __name__ == "__main__":
    main()
