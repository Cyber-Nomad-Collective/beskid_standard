"""Normalize `corelib_tests` entry imports and assertion call style.

- Inserts `use Testing.Assert;` when a file references `Testing.Assert` or `Assert.*`
- Inserts `use Core.Results;` when a file uses `Result::` or `Core.Results`
- Converts qualified `Testing.Assert.*` calls to unqualified `Assert.*`
- Sorts `use` lines after the doc comment block
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from common import ROOT

TESTS_SRC = ROOT / "beskid_corelib" / "tests" / "corelib_tests" / "src"

USE_LINE = re.compile(r"^\s*use\s+([^;]+);\s*$")
DOC_LINE = re.compile(r"^\s*///")
ASSERT_QUALIFIED = re.compile(r"Testing\.Assert\.(\w+)")

NEEDS_TESTING_ASSERT = re.compile(r"Testing\.Assert\.|(?<![.\w])Assert\.(Equal|True|False|Fail|Contains)\(")
NEEDS_CORE_RESULTS = re.compile(r"Result::|Core\.Results")


def has_use(source: str, module: str) -> bool:
    for match in USE_LINE.finditer(source):
        if match.group(1).strip() == module:
            return True
    return False


def split_doc_and_body(source: str) -> tuple[list[str], list[str]]:
    lines = source.splitlines(keepends=True)
    doc: list[str] = []
    body: list[str] = []
    in_doc = True
    for line in lines:
        if in_doc and (DOC_LINE.match(line) or line.strip() == ""):
            doc.append(line)
            if DOC_LINE.match(line):
                continue
            if line.strip() == "" and body:
                in_doc = False
                body.append(line)
            continue
        in_doc = False
        body.append(line)
    # Trim trailing blank lines from doc, keep one trailing blank if any doc lines exist
    while doc and doc[-1].strip() == "":
        doc.pop()
    return doc, body


def collect_use_lines(body: list[str]) -> tuple[list[str], list[str]]:
    uses: list[str] = []
    rest: list[str] = []
    for line in body:
        match = USE_LINE.match(line)
        if match:
            uses.append(match.group(1).strip())
        else:
            rest.append(line)
    return uses, rest


def normalize_file(source: str) -> str:
    changed = False
    text = source

    if ASSERT_QUALIFIED.search(text):
        text = ASSERT_QUALIFIED.sub(r"Assert.\1", text)
        changed = True

    doc, body = split_doc_and_body(text)
    uses, rest = collect_use_lines(body)
    body_text = "".join(rest)

    if NEEDS_TESTING_ASSERT.search(body_text) and not has_use(source, "Testing.Assert"):
        uses.append("Testing.Assert")
        changed = True

    if NEEDS_CORE_RESULTS.search(body_text) and not has_use(source, "Core.Results"):
        uses.append("Core.Results")
        changed = True

    if not changed and text == source:
        return source

    uses = sorted(set(uses))

    out: list[str] = []
    out.extend(doc)
    if doc:
        out.append("\n")
    for module in uses:
        out.append(f"use {module};\n")
    if uses:
        out.append("\n")
    out.extend(rest)
    result = "".join(out)
    if not result.endswith("\n"):
        result += "\n"
    return result


def iter_bd_files() -> list[Path]:
    return sorted(TESTS_SRC.rglob("*.bd"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any file would change.",
    )
    args = parser.parse_args()

    changed_files: list[Path] = []
    for path in iter_bd_files():
        original = path.read_text(encoding="utf-8")
        normalized = normalize_file(original)
        if normalized != original:
            changed_files.append(path)
            if not args.check:
                path.write_text(normalized, encoding="utf-8")

    if args.check and changed_files:
        for path in changed_files:
            print(f"would normalize: {path.relative_to(ROOT)}")
        raise SystemExit(1)

    if not args.check:
        print(f"normalized {len(changed_files)} file(s)")


if __name__ == "__main__":
    main()
