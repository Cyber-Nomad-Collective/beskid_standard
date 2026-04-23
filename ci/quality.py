"""Quality checks for beskid_corelib source layout."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORELIB = ROOT / "beskid_corelib"
MANIFEST = CORELIB / "Project.proj"
PRELUDE = CORELIB / "src" / "Prelude.bd"

REQUIRED_FILES = [
    "src/Core/Results.bd",
    "src/Core/ErrorHandling.bd",
    "src/Core/String.bd",
    "src/Testing/Contracts.bd",
    "src/Testing/Assertions.bd",
    "src/System/IO.bd",
    "src/Prelude.bd",
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
        raise SystemExit(f"Missing corelib directory: {CORELIB}")
    if not MANIFEST.is_file():
        raise SystemExit(f"Missing manifest: {MANIFEST}")
    if not PRELUDE.is_file():
        raise SystemExit(f"Missing prelude: {PRELUDE}")

    content = MANIFEST.read_text(encoding="utf-8")
    name = _project_field(content, "name")
    if name != "beskid_corelib":
        raise SystemExit(f"Project name must be beskid_corelib, got: {name!r}")

    version = _project_field(content, "version")
    if not version:
        raise SystemExit("Project.proj is missing version")

    for relative in REQUIRED_FILES:
        path = CORELIB / relative
        if not path.is_file():
            raise SystemExit(f"Missing required file: {path}")

    if 'target "CoreLib"' not in content:
        raise SystemExit('Project.proj must declare `target "CoreLib"` (canonical default library target)')

    print(f"quality OK: beskid_corelib manifest version {version}")


if __name__ == "__main__":
    main()
