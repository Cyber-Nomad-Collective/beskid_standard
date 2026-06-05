"""Run all `corelib_tests` targets via `beskid test` (rolling CLI from releases)."""

from __future__ import annotations

import os
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
    all_targets = parse_project_targets(TESTS_MANIFEST)
    if not all_targets:
        raise SystemExit(f"No test targets found in {TESTS_MANIFEST}")

    _clear_stale_obj_trees()
    filter_raw = os.environ.get("BESKID_CORELIB_TEST_TARGETS", "").strip()
    if filter_raw:
        print(
            f"[test] running filtered targets ({filter_raw}) with {cli} "
            "(BESKID_CORELIB_TEST_TARGETS)"
        )
    else:
        print(f"[test] running {len(all_targets)} target(s) with {cli}")

    print("[test] beskid test --all-targets --plain")
    result = subprocess.run(
        [
            str(cli),
            "test",
            "--project",
            str(TESTS_MANIFEST),
            "--all-targets",
            "--plain",
        ],
        cwd=TESTS_PROJECT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("corelib_tests failed")

    print(f"[test] OK: targets passed")


if __name__ == "__main__":
    main()
