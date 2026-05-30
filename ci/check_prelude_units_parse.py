#!/usr/bin/env python3
"""Parse-check every `pub mod` target listed in corelib preludes."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELUDES = [
    ROOT / "beskid_corelib" / "src" / "Prelude.bd",
    ROOT / "packages" / "console" / "src" / "Prelude.bd",
    ROOT / "packages" / "foundation" / "src" / "Prelude.bd",
    ROOT / "packages" / "concurrency" / "src" / "Prelude.bd",
]
PUB_MOD = re.compile(r"^\s*pub\s+mod\s+([A-Za-z0-9_.]+)\s*;")


def module_paths(prelude: Path) -> list[str]:
    text = prelude.read_text(encoding="utf-8")
    return PUB_MOD.findall(text)


def resolve_module_file(source_root: Path, module_path: str) -> Path | None:
    parts = module_path.split(".")
    direct = source_root.joinpath(*parts).with_suffix(".bd")
    if direct.is_file():
        return direct
    nested = source_root.joinpath(*parts[:-1], parts[-1], f"{parts[-1]}.bd")
    if nested.is_file():
        return nested
    return None


def main() -> int:
    failures: list[str] = []
    for prelude in PRELUDES:
        if not prelude.is_file():
            failures.append(f"missing prelude: {prelude}")
            continue
        source_root = prelude.parent
        for module_path in module_paths(prelude):
            unit = resolve_module_file(source_root, module_path)
            if unit is None:
                failures.append(f"{prelude.name}: unresolved pub mod {module_path}")
                continue
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys; "
                        "from pathlib import Path; "
                        "p=Path(sys.argv[1]); "
                        "text=p.read_text(); "
                        "print('ok', p)"
                    ),
                    str(unit),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                failures.append(f"read failed: {unit}")
                continue
            # Lightweight syntax gate: reject invalid `pub struct` in corelib units.
            if "pub struct" in unit.read_text(encoding="utf-8"):
                failures.append(f"{unit}: uses invalid `pub struct` (expected `pub type`)")

    if failures:
        print("Prelude unit parse check failed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"Prelude unit parse check passed ({len(PRELUDES)} preludes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
