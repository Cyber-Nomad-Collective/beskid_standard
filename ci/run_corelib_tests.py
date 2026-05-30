"""Run all `corelib_tests` targets via `beskid test` (rolling CLI from releases)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from common import ROOT, ensure_cli, parse_project_targets

TESTS_PROJECT = ROOT / "beskid_corelib" / "tests" / "corelib_tests"
TESTS_MANIFEST = TESTS_PROJECT / "Project.proj"
_TARGET_FILTER = re.compile(r"^\s*([^,\s]+)\s*$")


def _selected_targets(all_targets: list[str]) -> list[str]:
    raw = os.environ.get("BESKID_CORELIB_TEST_TARGETS", "").strip()
    if not raw:
        return all_targets
    wanted = {
        match.group(1)
        for part in raw.split(",")
        if (match := _TARGET_FILTER.match(part.strip()))
    }
    missing = wanted - set(all_targets)
    if missing:
        raise SystemExit(
            f"BESKID_CORELIB_TEST_TARGETS unknown targets: {', '.join(sorted(missing))}"
        )
    return [name for name in all_targets if name in wanted]


def _clear_stale_obj_trees() -> None:
    if os.environ.get("BESKID_CLEAR_OBJ", "").strip() in ("1", "true", "yes"):
        for obj_dir in (TESTS_PROJECT / "obj", TESTS_PROJECT.parent / "obj"):
            if obj_dir.is_dir():
                print(f"[test] removing stale artifacts {obj_dir}")
                shutil.rmtree(obj_dir)
        return
    cache_dir = TESTS_PROJECT / "obj" / "beskid" / "cache"
    for obj_dir in (TESTS_PROJECT / "obj", TESTS_PROJECT.parent / "obj"):
        if not obj_dir.is_dir():
            continue
        for child in obj_dir.iterdir():
            if child.name == "beskid":
                continue
            if child.is_dir():
                print(f"[test] removing stale artifacts {child}")
                shutil.rmtree(child)
            elif child.is_file():
                child.unlink(missing_ok=True)
    if cache_dir.is_dir():
        print(f"[test] preserving unit cache at {cache_dir}")


def main() -> None:
    if not TESTS_MANIFEST.is_file():
        raise SystemExit(f"Missing corelib_tests manifest: {TESTS_MANIFEST}")

    cli = ensure_cli()
    targets = _selected_targets(parse_project_targets(TESTS_MANIFEST))
    if not targets:
        raise SystemExit(f"No test targets found in {TESTS_MANIFEST}")

    _clear_stale_obj_trees()
    print(f"[test] running {len(targets)} target(s) with {cli}")

    failures: list[str] = []
    for target in targets:
        print(f"[test] beskid test --target {target}")
        result = subprocess.run(
            [
                str(cli),
                "test",
                "--project",
                str(TESTS_MANIFEST),
                "--target",
                target,
                "--plain",
            ],
            cwd=TESTS_PROJECT,
            check=False,
        )
        if result.returncode != 0:
            failures.append(target)

    if failures:
        raise SystemExit(
            f"corelib_tests failed for {len(failures)} target(s): {', '.join(failures)}"
        )

    print(f"[test] OK: {len(targets)} target(s) passed")


if __name__ == "__main__":
    main()
