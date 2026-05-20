"""Quality checks for the Beskid corelib workspace (aggregate `beskid_corelib` + `packages/*`)."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORELIB = ROOT / "beskid_corelib"
MANIFEST = CORELIB / "Project.proj"
PRELUDE = CORELIB / "src" / "Prelude.bd"
WORKSPACE_MANIFEST = ROOT / "Workspace.proj"
WORKSPACE_PACKAGE_JSON = ROOT / "workspace.package.json"

WORKSPACE_MEMBERS = (
    ("corelib", "beskid_corelib"),
    ("corelib_foundation", "packages/foundation"),
    ("corelib_runtime", "packages/runtime"),
    ("corelib_compiler_sdk", "packages/compiler-sdk"),
    ("corelib_console", "packages/console"),
    ("corelib_concurrency", "packages/concurrency"),
)

# Key hand-authored sources that must remain present after workspace splits.
REQUIRED_FILES = [
    ROOT / "packages/foundation/src/Core/Results.bd",
    ROOT / "packages/foundation/src/Core/ErrorHandling.bd",
    ROOT / "packages/foundation/src/Core/String.bd",
    ROOT / "packages/foundation/src/Testing/Contracts.bd",
    ROOT / "packages/foundation/src/Testing/Assertions.bd",
    ROOT / "packages/runtime/src/System/Input.bd",
    ROOT / "packages/runtime/src/System/Output.bd",
    ROOT / "packages/foundation/src/Prelude.bd",
]


def _project_field(content: str, key: str) -> str | None:
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip('"')
    return None


def main() -> None:
    if not CORELIB.is_dir():
        raise SystemExit(f"Missing corelib package directory: {CORELIB}")
    if not MANIFEST.is_file():
        raise SystemExit(f"Missing manifest: {MANIFEST}")
    if not PRELUDE.is_file():
        raise SystemExit(f"Missing prelude: {PRELUDE}")
    if not WORKSPACE_MANIFEST.is_file():
        raise SystemExit(f"Missing workspace manifest: {WORKSPACE_MANIFEST}")
    if not WORKSPACE_PACKAGE_JSON.is_file():
        raise SystemExit(f"Missing workspace publish metadata: {WORKSPACE_PACKAGE_JSON}")

    content = MANIFEST.read_text(encoding="utf-8")
    name = _project_field(content, "name")
    if name != "corelib":
        raise SystemExit(f"Project name must be corelib, got: {name!r}")

    version = _project_field(content, "version")
    if not version:
        raise SystemExit("Project.proj is missing version")

    workspace_text = WORKSPACE_MANIFEST.read_text(encoding="utf-8")
    if _project_field(workspace_text, "name") != "corelib":
        raise SystemExit("Workspace.proj workspace name must be corelib")

    workspace_package = json.loads(WORKSPACE_PACKAGE_JSON.read_text(encoding="utf-8"))
    if workspace_package.get("schema") != "beskid.workspace.package.v1":
        raise SystemExit("workspace.package.json schema must be beskid.workspace.package.v1")
    members = workspace_package.get("members")
    if not isinstance(members, dict):
        raise SystemExit("workspace.package.json must declare members")

    for registry_name, source_rel in WORKSPACE_MEMBERS:
        member_manifest = ROOT / source_rel / "Project.proj"
        if not member_manifest.is_file():
            raise SystemExit(f"Missing member manifest: {member_manifest}")
        member_name = _project_field(member_manifest.read_text(encoding="utf-8"), "name")
        if member_name != registry_name:
            raise SystemExit(
                f"{member_manifest}: project.name must be {registry_name!r}, got {member_name!r}"
            )
        readme = ROOT / source_rel / "README.md"
        if not readme.is_file():
            raise SystemExit(f"Missing member README.md: {readme}")
        member_id = next(
            (key for key, value in members.items() if value.get("package") == registry_name),
            None,
        )
        if member_id is None:
            raise SystemExit(
                f"workspace.package.json is missing a member entry for registry package {registry_name!r}"
            )

    for path in REQUIRED_FILES:
        if not path.is_file():
            raise SystemExit(f"Missing required file: {path}")

    if 'target "CoreLib"' not in content:
        raise SystemExit('Project.proj must declare `target "CoreLib"` (canonical default library target)')

    print(f"quality OK: corelib workspace manifest version {version}")


if __name__ == "__main__":
    main()
