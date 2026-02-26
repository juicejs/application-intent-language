#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PACKAGES = ROOT / "registry" / "packages"
HEADER_RE = re.compile(
    r"^AIL:\s+([a-z0-9]+(?:\.[a-z0-9]+)*)#(intent|schema|flow|contract|persona|mapping)@([0-9]+\.[0-9]+)$"
)
FEATURE_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")
LEGACY_TOKENS = (":::AIL_METADATA", "FEATURE:", "FACET:", "VERSION:")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def check_package_dir(pkg_dir: Path) -> None:
    manifest_path = pkg_dir / "package.json"
    if not manifest_path.exists():
        fail(f"{pkg_dir}: missing package.json")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{manifest_path}: invalid JSON ({exc})")

    for key in ("name", "version", "summary", "files"):
        if key not in manifest:
            fail(f"{manifest_path}: missing required key '{key}'")

    name = manifest["name"]
    version = manifest["version"]
    files = manifest["files"]

    if not isinstance(name, str) or not FEATURE_RE.match(name):
        fail(f"{manifest_path}: invalid 'name', expected lowercase namespace segments separated by dots")
    if pkg_dir.name != name:
        fail(f"{manifest_path}: directory name '{pkg_dir.name}' must match name '{name}'")
    if not isinstance(version, str) or not VERSION_RE.match(version):
        fail(f"{manifest_path}: invalid 'version', expected x.y")
    if not isinstance(files, list) or not files:
        fail(f"{manifest_path}: 'files' must be a non-empty array")

    for rel in files:
        if not isinstance(rel, str) or not rel.endswith(".ail"):
            fail(f"{manifest_path}: each files entry must be a .ail path, got '{rel}'")
        fpath = pkg_dir / rel
        if not fpath.exists():
            fail(f"{manifest_path}: listed file does not exist: {rel}")
        validate_ail_source(fpath, expected_feature=name, expected_version=version)


def validate_ail_source(path: Path, expected_feature: str, expected_version: str) -> None:
    raw = path.read_text(encoding="utf-8")
    for token in LEGACY_TOKENS:
        if token in raw:
            fail(f"{path}: legacy metadata token '{token}' is not allowed")

    first_line = raw.splitlines()[0].strip() if raw.splitlines() else ""
    m = HEADER_RE.match(first_line)
    if not m:
        fail(f"{path}: first line must match AIL header grammar")

    feature, _facet, version = m.groups()
    if feature != expected_feature:
        fail(f"{path}: header feature '{feature}' does not match package name '{expected_feature}'")
    if version != expected_version:
        fail(f"{path}: header version '{version}' does not match package version '{expected_version}'")


def main() -> None:
    if not REGISTRY_PACKAGES.exists():
        fail(f"missing directory: {REGISTRY_PACKAGES}")

    package_dirs = sorted([p for p in REGISTRY_PACKAGES.iterdir() if p.is_dir()])
    if not package_dirs:
        fail("registry/packages must contain at least one package directory")

    for pkg_dir in package_dirs:
        check_package_dir(pkg_dir)

    print(f"[OK] Validated {len(package_dirs)} package(s)")


if __name__ == "__main__":
    main()
