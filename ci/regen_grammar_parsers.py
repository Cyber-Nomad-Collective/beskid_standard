"""Regenerate foundation grammar parsers via corelib_pest_gen mod rebuild.

Preferred path once Beskid `Core.Text.Pest` emit is AOT-ready:
  beskid mod rebuild --plain mods/corelib_pest_gen/corelib_pest_gen.bproj

Until then, falls back to the Rust `beskid_pest_gen` bridge (`emit_grammar`) so
checked-in `Generated.g.bd` keeps PascalCase/camelCase naming (PARSER-005).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from common import ROOT, ensure_cli

MOD_DIR = ROOT / "mods" / "corelib_pest_gen"
MOD_MANIFEST = MOD_DIR / "corelib_pest_gen.bproj"
LAYOUT = MOD_DIR / "generate.layout.json"
FOUNDATION_DIR = ROOT / "packages" / "foundation"
GRAMMAR = FOUNDATION_DIR / "grammars" / "regex.pest"
GENERATED = FOUNDATION_DIR / ".generated" / "Core" / "Text" / "Regex" / "Generated.g.bd"
COMPILER_ROOT = ROOT.parent


def copy_layout_checked_in() -> None:
    if not LAYOUT.is_file():
        raise SystemExit(f"Missing generate layout: {LAYOUT}")
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    for entry in layout["files"]:
        src = GENERATED
        if not src.is_file():
            raise SystemExit(f"Missing checked-in grammar output: {src}")
        rel = entry.get("path")
        if rel:
            dst = MOD_DIR / "Generated" / rel
        else:
            module_path = entry.get("modulePath", "Core.Text.Regex.Generated")
            file_name = entry.get("fileName", "Generated")
            rel_parts = module_path.split(".")
            dst = MOD_DIR / "Generated" / Path(*rel_parts) / f"{file_name}.g.bd"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def try_mod_rebuild(cli: Path) -> bool:
    if not MOD_MANIFEST.is_file():
        return False
    rebuild_cmd = [str(cli), "mod", "rebuild", "--plain", str(MOD_MANIFEST)]
    print(f"[regen] {' '.join(rebuild_cmd)}")
    rebuild = subprocess.run(rebuild_cmd, cwd=MOD_DIR, check=False)
    return rebuild.returncode == 0


def emit_via_rust_bridge() -> None:
    if not GRAMMAR.is_file():
        raise SystemExit(f"Missing grammar source: {GRAMMAR}")
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "cargo",
        "run",
        "-q",
        "-p",
        "beskid_pest_gen",
        "--bin",
        "emit_grammar",
        "--",
        str(GRAMMAR),
        str(GENERATED),
        "regex",
    ]
    print(f"[regen] {' '.join(cmd)} (cwd={COMPILER_ROOT})")
    subprocess.run(cmd, cwd=COMPILER_ROOT, check=True)


def main() -> None:
    cli = ensure_cli()
    if try_mod_rebuild(cli):
        print("[regen] mod rebuild OK; sync Generated/ from layout when Beskid emit lands")
        copy_layout_checked_in()
    else:
        print("[regen] mod rebuild unavailable; using beskid_pest_gen Rust bridge")
        emit_via_rust_bridge()
    print(f"[regen] OK: grammar parser at {GENERATED}")


if __name__ == "__main__":
    main()
