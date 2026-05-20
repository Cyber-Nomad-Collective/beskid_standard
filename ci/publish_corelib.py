"""Publish the Beskid corelib workspace (all members) to pckg via workspace bundle upload."""

from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_MANIFEST = ROOT / "Workspace.proj"
WORKSPACE_PACKAGE_JSON = ROOT / "workspace.package.json"
REPOSITORY_BASE = (
    "https://github.com/Cyber-Nomad-Collective/beskid_compiler/tree/main/compiler/corelib"
)
_DEFAULT_CLI_DOWNLOAD_URL = (
    "https://github.com/Cyber-Nomad-Collective/beskid_compiler/releases/download/"
    "cli-latest/beskid-linux-amd64"
)
_SKIP_DIR_NAMES = frozenset(
    {
        "obj",
        "bin",
        ".git",
        ".ci-tools",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
    }
)
_SKIP_FILE_NAMES = frozenset({".DS_Store"})


@dataclass(frozen=True)
class WorkspacePackageMeta:
    registry_name: str
    member_id: str
    source_rel: str
    description: str
    tags: tuple[str, ...]


WORKSPACE_PACKAGES: tuple[WorkspacePackageMeta, ...] = (
    WorkspacePackageMeta(
        "corelib",
        "corelib",
        "beskid_corelib",
        (
            "Beskid standard library aggregate: prelude and re-exports of foundation, "
            "runtime, console, concurrency, and compiler SDK packages."
        ),
        ("corelib", "stdlib", "beskid", "standard-library"),
    ),
    WorkspacePackageMeta(
        "corelib_foundation",
        "foundation",
        "packages/foundation",
        "Low-level primitives shared by Beskid corelib workspace packages (collections, results, strings, testing helpers).",
        ("corelib", "foundation", "beskid", "stdlib"),
    ),
    WorkspacePackageMeta(
        "corelib_runtime",
        "runtime",
        "packages/runtime",
        "Runtime and syscall surfaces for Beskid (`System`, process, and I/O helpers).",
        ("corelib", "runtime", "beskid", "stdlib", "syscall"),
    ),
    WorkspacePackageMeta(
        "corelib_compiler_sdk",
        "compiler_sdk",
        "packages/compiler-sdk",
        "Typed compiler Mod SDK facades (`Beskid.Compiler.*`, `Beskid.Syntax`) for `type: Mod` projects.",
        ("corelib", "compiler", "mod-sdk", "beskid"),
    ),
    WorkspacePackageMeta(
        "corelib_console",
        "console",
        "packages/console",
        "Terminal and ANSI helpers (`Console`, `Ansi`) built on corelib runtime I/O.",
        ("corelib", "console", "beskid", "stdlib"),
    ),
    WorkspacePackageMeta(
        "corelib_concurrency",
        "concurrency",
        "packages/concurrency",
        "Cooperative concurrency primitives (`Fiber`, channels) and `System.Threading` OS-thread helpers.",
        ("corelib", "concurrency", "beskid", "stdlib"),
    ),
)

# Doc generation order: path dependencies must exist on disk before dependents compile.
_DOC_GENERATION_ORDER: tuple[str, ...] = (
    "packages/foundation",
    "packages/compiler-sdk",
    "packages/concurrency",
    "packages/runtime",
    "packages/console",
    "beskid_corelib",
)


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


def _default_icon_url(base_url: str, package_name: str) -> str:
    override = os.environ.get("BESKID_CORELIB_ICON_URL", "").strip()
    if override:
        return override
    root = base_url.rstrip("/") + "/"
    slug = "corelib.svg" if package_name == "corelib" else "corelib.svg"
    return urllib.parse.urljoin(root, f"package-icons/{slug}")


def _upsert_package(base_url: str, api_key: str, meta: WorkspacePackageMeta) -> None:
    root = base_url.rstrip("/") + "/"
    url = urllib.parse.urljoin(root, "api/packages")
    payload = {
        "name": meta.registry_name,
        "description": meta.description,
        "category": "Library",
        "repositoryUrl": f"{REPOSITORY_BASE}/{meta.source_rel}",
        "websiteUrl": "https://beskid-lang.org",
        "tags": list(meta.tags),
        "isPublic": True,
        "submitForReview": False,
        "reviewReason": None,
        "iconUrl": _default_icon_url(base_url, meta.registry_name),
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
            f"Failed to upsert {meta.registry_name} metadata (HTTP {exc.code}): {detail or exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach pckg at {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        print(f"[publish] upsert {meta.registry_name}: unexpected non-JSON response: {body[:500]!r}")
        return
    if not parsed.get("success", True):
        raise SystemExit(f"Upsert {meta.registry_name} failed: {parsed.get('message', body)}")
    print(f"[publish] ensured {meta.registry_name} package metadata (upsert ok)")


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


def _resolve_corelib_workspace_root() -> Path:
    override = os.environ.get("BESKID_CORELIB_ROOT", "").strip()
    if override:
        root = Path(override).expanduser()
        if not root.is_absolute():
            root = (ROOT / root).resolve()
    else:
        root = ROOT

    manifest = root / "beskid_corelib" / "Project.proj"
    if not manifest.is_file():
        raise SystemExit(
            "BESKID_CORELIB_ROOT must point to a workspace tree containing "
            f"`beskid_corelib/Project.proj`, got: {root}"
        )
    if not (root / "Workspace.proj").is_file():
        raise SystemExit(f"Workspace.proj not found under corelib root: {root}")
    if not (root / "workspace.package.json").is_file():
        raise SystemExit(f"workspace.package.json not found under corelib root: {root}")
    return root


def _validate_workspace_packages(workspace_root: Path) -> None:
    workspace_text = (workspace_root / "Workspace.proj").read_text(encoding="utf-8")
    workspace_name = _project_field(workspace_text, "name")
    if workspace_name != "corelib":
        raise SystemExit(f"Workspace.proj name must be 'corelib', got {workspace_name!r}")

    for meta in WORKSPACE_PACKAGES:
        manifest = workspace_root / meta.source_rel / "Project.proj"
        if not manifest.is_file():
            raise SystemExit(f"Missing Project.proj for {meta.registry_name}: {manifest}")
        project_name = _project_field(manifest.read_text(encoding="utf-8"), "name")
        if project_name != meta.registry_name:
            raise SystemExit(
                f"{manifest}: project.name must be {meta.registry_name!r}, got {project_name!r}"
            )
        readme = workspace_root / meta.source_rel / "README.md"
        if not readme.is_file():
            raise SystemExit(f"Missing README.md for {meta.registry_name}: {readme}")


def _generate_member_docs(
    cli_bin: Path,
    base_url: str,
    workspace_root: Path,
) -> None:
    pack_dir = workspace_root / ".ci-publish-pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    common = [str(cli_bin), "pckg", "--base-url", base_url]
    pack_env = {**os.environ, "BESKID_CORELIB_ROOT": str(workspace_root)}

    for source_rel in _DOC_GENERATION_ORDER:
        meta = next(m for m in WORKSPACE_PACKAGES if m.source_rel == source_rel)
        source = workspace_root / source_rel
        artifact = pack_dir / f"{meta.registry_name}.bpk"
        if artifact.exists():
            artifact.unlink()
        print(f"[publish] generating docs via pack for {meta.registry_name} ({source_rel})")
        result = subprocess.run(
            common
            + [
                "pack",
                "--package",
                meta.registry_name,
                "--source",
                str(source),
                "--output",
                str(artifact),
            ],
            check=True,
            cwd=workspace_root,
            capture_output=True,
            text=True,
            env=pack_env,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        artifact.unlink(missing_ok=True)


def _should_skip_relative(rel_posix: str) -> bool:
    path = PurePosixPath(rel_posix)
    if path.name in _SKIP_FILE_NAMES:
        return True
    if any(part in _SKIP_DIR_NAMES for part in path.parts):
        return True
    if rel_posix.endswith(".bpk"):
        return True
    return False


def _build_workspace_bundle(workspace_root: Path, output: Path) -> None:
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(workspace_root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(workspace_root).as_posix()
            if _should_skip_relative(rel):
                continue
            archive.write(path, rel)
    print(f"[publish] workspace bundle: {output} ({output.stat().st_size} bytes)")


def _encode_multipart(
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
) -> tuple[bytes, str]:
    boundary = f"beskid-{uuid.uuid4().hex}"
    lines: list[bytes] = []

    for name, value in fields.items():
        lines.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )

    for name, (filename, content, content_type) in files.items():
        lines.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                ).encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                content,
                b"\r\n",
            ]
        )

    lines.extend([f"--{boundary}--\r\n".encode()])
    body = b"".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


def _publish_workspace_bundle(
    base_url: str,
    api_key: str,
    bundle_path: Path,
    version_bump: str,
) -> list[dict[str, object]]:
    root = base_url.rstrip("/") + "/"
    url = urllib.parse.urljoin(root, "api/workspaces/publish")
    bundle_bytes = bundle_path.read_bytes()
    body, content_type = _encode_multipart(
        {"versionBump": version_bump},
        {
            "artifact": (
                "workspace.bundle.zip",
                bundle_bytes,
                mimetypes.guess_type("workspace.bundle.zip")[0] or "application/zip",
            )
        },
    )
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Accept": "application/json",
            "X-API-Key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            response_body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise SystemExit(
            f"Workspace publish failed (HTTP {exc.code}): {detail or exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to reach pckg at {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Workspace publish returned non-JSON: {response_body[:500]!r}") from exc

    if not parsed.get("success"):
        raise SystemExit(f"Workspace publish failed: {parsed.get('message', response_body)}")

    packages = parsed.get("packages")
    if not isinstance(packages, list) or not packages:
        raise SystemExit(f"Workspace publish succeeded but returned no packages: {response_body}")

    return packages


def main() -> None:
    api_key = _require("BESKID_PCKG_API_KEY")
    base_url = os.environ.get("BESKID_PCKG_BASE_URL", "https://pckg.beskid-lang.org").strip()
    version_bump = os.environ.get("BESKID_PCKG_VERSION_BUMP", "patch").strip().lower()
    if version_bump not in {"patch", "minor", "major"}:
        raise SystemExit("BESKID_PCKG_VERSION_BUMP must be patch, minor, or major")

    workspace_root = _resolve_corelib_workspace_root()
    _validate_workspace_packages(workspace_root)

    for meta in WORKSPACE_PACKAGES:
        _upsert_package(base_url, api_key, meta)

    cli_bin = _ensure_cli()
    _generate_member_docs(cli_bin, base_url, workspace_root)

    bundle_path = workspace_root / ".ci-publish-workspace.bundle.zip"
    _build_workspace_bundle(workspace_root, bundle_path)

    published = _publish_workspace_bundle(base_url, api_key, bundle_path, version_bump)
    for entry in published:
        if not isinstance(entry, dict):
            continue
        member_id = entry.get("memberId", "?")
        package_name = entry.get("packageName", "?")
        version = entry.get("version", "?")
        print(f"PCKG_PUBLISHED_VERSION={package_name}@{version}")
        print(f"[publish] {member_id} -> {package_name} {version} (registry-assigned)")

    print(f"Published {len(published)} workspace package(s) to {base_url}")

    if os.environ.get("CI_KEEP_ARTIFACT", "").strip().lower() not in {"1", "true", "yes"}:
        bundle_path.unlink(missing_ok=True)
        shutil.rmtree(workspace_root / ".ci-publish-pack", ignore_errors=True)
    if os.environ.get("CI_KEEP_TOOLS", "").strip().lower() not in {"1", "true", "yes"}:
        shutil.rmtree(ROOT / ".ci-tools", ignore_errors=True)


if __name__ == "__main__":
    main()
