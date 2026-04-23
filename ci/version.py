"""Resolve release version mirroring Beskid VSCode semver behavior."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "beskid_corelib" / "Project.proj"

TAG_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _split(tag: str) -> tuple[int, int, int]:
    match = TAG_RE.match(tag)
    if not match:
        raise SystemExit(f"Tag `{tag}` is not semver (expected vMAJOR.MINOR.PATCH)")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def _project_field(content: str, key: str) -> str | None:
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip('"')
    return None


def _manifest_version_fallback() -> str:
    if not MANIFEST.is_file():
        raise SystemExit(f"No semver git tags found and missing manifest: {MANIFEST}")
    content = MANIFEST.read_text(encoding="utf-8")
    version = _project_field(content, "version")
    if not version:
        raise SystemExit("Project.proj is missing version (fallback)")
    return version


def resolve_version() -> str:
    tag_ref = os.environ.get("GITHUB_REF_NAME", "").strip()
    if os.environ.get("GITHUB_REF_TYPE", "").strip() == "tag" and TAG_RE.match(tag_ref):
        return tag_ref.removeprefix("v")

    try:
        latest_tag = subprocess.check_output(
            [
                "git",
                "describe",
                "--tags",
                "--abbrev=0",
                "--match",
                "v[0-9]*.[0-9]*.[0-9]*",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return _manifest_version_fallback()

    major, minor, patch = _split(latest_tag)
    commits_since = int(_git("rev-list", "--count", f"{latest_tag}..HEAD"))
    if commits_since <= 0:
        return f"{major}.{minor}.{patch}"
    return f"{major}.{minor}.{patch + commits_since}"


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT", "").strip()
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> None:
    version = resolve_version()
    print(version)
    write_output("version", version)


if __name__ == "__main__":
    main()
