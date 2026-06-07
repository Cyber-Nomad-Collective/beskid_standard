"""Quality checks for the Beskid corelib workspace (aggregate `beskid_corelib` + `packages/*`)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORELIB = ROOT / "beskid_corelib"
WORKSPACE_MANIFEST = ROOT / "CoreLib.bws"

WORKSPACE_MEMBERS = (
    ("corelib", "beskid_corelib"),
    ("corelib_foundation", "packages/foundation"),
    ("corelib_runtime", "packages/runtime"),
    ("corelib_compiler_sdk", "packages/compiler-sdk"),
    ("corelib_console", "packages/console"),
    ("corelib_concurrency", "packages/concurrency"),
)

REQUIRED_FILES = [
    ROOT / "packages/foundation/src/Core/Results.bd",
    ROOT / "packages/foundation/src/Core/ErrorHandling.bd",
    ROOT / "packages/foundation/src/Core/String.bd",
    ROOT / "packages/foundation/src/Testing/Contracts.bd",
    ROOT / "packages/foundation/src/Testing/Assertions.bd",
    ROOT / "packages/runtime/src/System/Input.bd",
    ROOT / "packages/runtime/src/System/Output.bd",
]

_MEMBER_BLOCK = re.compile(r'member\s+"([^"]+)"\s*\{([^}]*)\}', re.DOTALL)


def _project_field(content: str, key: str) -> str | None:
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip('"')
    return None


def _member_package_map(workspace_text: str) -> dict[str, str]:
    packages: dict[str, str] = {}
    for _member_id, body in _MEMBER_BLOCK.findall(workspace_text):
        package = _project_field(body, "package")
        if package:
            packages[package] = _project_field(body, "path") or ""
    return packages


def _discover_project_manifest(project_dir: Path) -> Path:
    matches = sorted(project_dir.glob("*.bproj"))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one `.bproj` in {project_dir}, found {len(matches)}")
    return matches[0]


def main() -> None:
    if not CORELIB.is_dir():
        raise SystemExit(f"Missing corelib package directory: {CORELIB}")
    manifest = _discover_project_manifest(CORELIB)
    if not WORKSPACE_MANIFEST.is_file():
        raise SystemExit(f"Missing workspace manifest: {WORKSPACE_MANIFEST}")

    content = manifest.read_text(encoding="utf-8")
    name = _project_field(content, "name")
    if name != "corelib":
        raise SystemExit(f"Project name must be corelib, got: {name!r}")

    project_type = _project_field(content, "type")
    if project_type != "Aggregate":
        raise SystemExit(f"Aggregate corelib manifest must set type = Aggregate, got: {project_type!r}")

    version = _project_field(content, "version")
    if not version:
        raise SystemExit(f"{manifest.name} is missing version")

    workspace_text = WORKSPACE_MANIFEST.read_text(encoding="utf-8")
    if _project_field(workspace_text, "name") != "corelib":
        raise SystemExit("CoreLib.bws workspace name must be corelib")

    member_packages = _member_package_map(workspace_text)
    if not member_packages:
        raise SystemExit("CoreLib.bws must declare member blocks with package keys")

    for registry_name, source_rel in WORKSPACE_MEMBERS:
        member_manifest = _discover_project_manifest(ROOT / source_rel)
        member_name = _project_field(member_manifest.read_text(encoding="utf-8"), "name")
        if member_name != registry_name:
            raise SystemExit(
                f"{member_manifest}: project.name must be {registry_name!r}, got {member_name!r}"
            )
        readme = ROOT / source_rel / "README.md"
        if not readme.is_file():
            readme = ROOT / source_rel / "readme.md"
        if not readme.is_file():
            raise SystemExit(f"Missing member README for {registry_name}: {readme}")
        if registry_name not in member_packages:
            raise SystemExit(
                f"CoreLib.bws is missing a member entry for registry package {registry_name!r}"
            )

    for path in REQUIRED_FILES:
        if not path.is_file():
            raise SystemExit(f"Missing required file: {path}")

    print(f"quality OK: corelib workspace manifest version {version}")


if __name__ == "__main__":
    main()
