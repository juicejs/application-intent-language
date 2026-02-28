#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PACKAGES = ROOT / "registry" / "packages"
REGISTRY_INDEX = ROOT / "registry" / "index.json"
HEADER_RE = re.compile(
    r"^AIM:\s+([a-z0-9]+(?:\.[a-z0-9]+)*)#(intent|schema|flow|contract|persona|view|event|mapping)@([0-9]+\.[0-9]+)$"
)
FEATURE_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")
LEGACY_TOKENS = (":::AIL_METADATA", ":::AIM_METADATA", "FEATURE:", "FACET:", "VERSION:")
INCLUDES_START_RE = re.compile(r"^\s*INCLUDES\s*\{\s*$")
INCLUDES_ENTRY_RE = re.compile(r'^\s*(schema|flow|contract|persona|view|event)\s*:\s*"([^"]+)"\s*$')
INCLUDES_END_RE = re.compile(r"^\s*}\s*$")
FACETS = ("intent", "schema", "flow", "contract", "persona", "view", "event", "mapping")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def parse_header(path: Path) -> tuple[str, str, str]:
    raw = path.read_text(encoding="utf-8")
    for token in LEGACY_TOKENS:
        if token in raw:
            fail(f"{path}: legacy metadata token '{token}' is not allowed")
    lines = raw.splitlines()
    first_line = lines[0].strip() if lines else ""
    m = HEADER_RE.match(first_line)
    if not m:
        fail(f"{path}: first line must match AIM header grammar")
    return m.group(1), m.group(2), m.group(3)


def derive_identity_from_relpath(rel_path: Path) -> tuple[str, str]:
    if rel_path.suffix != ".intent":
        fail(f"{rel_path}: source path must end with .intent")

    if len(rel_path.parts) == 1:
        stem_parts = rel_path.name[:-len(".intent")].split(".")
        if stem_parts[-1] in FACETS:
            if len(stem_parts) < 2:
                fail(f"{rel_path}: flat source filename must be <feature>.<facet>.intent")
            feature = ".".join(stem_parts[:-1])
            facet = stem_parts[-1]
        else:
            feature = ".".join(stem_parts)
            facet = "intent"
    else:
        feature = ".".join(rel_path.parts[:-1])
        facet = rel_path.stem

    if not FEATURE_RE.match(feature):
        fail(f"{rel_path}: derived feature '{feature}' is invalid")
    if facet not in FACETS:
        fail(f"{rel_path}: derived facet '{facet}' is invalid")
    return feature, facet


def validate_source_file(
    path: Path,
    *,
    package_root: Path,
    expected_feature: str | None = None,
    expected_version: str | None = None,
) -> tuple[str, str, str]:
    feature, facet, version = parse_header(path)
    rel_path = path.relative_to(package_root)
    path_feature, path_facet = derive_identity_from_relpath(rel_path)

    if path_feature != feature:
        fail(f"{path}: path-derived feature '{path_feature}' does not match header feature '{feature}'")
    if path_facet != facet:
        fail(f"{path}: path-derived facet '{path_facet}' does not match header facet '{facet}'")
    if expected_feature is not None and feature != expected_feature:
        fail(f"{path}: header feature '{feature}' does not match package name '{expected_feature}'")
    if expected_version is not None and version != expected_version:
        fail(f"{path}: header version '{version}' does not match package version '{expected_version}'")
    return feature, facet, version


def validate_entry_file(path: Path, expected_feature: str, expected_version: str) -> None:
    feature, facet, _version = validate_source_file(
        path,
        package_root=REGISTRY_PACKAGES / expected_feature,
        expected_feature=expected_feature,
        expected_version=expected_version,
    )
    if feature != expected_feature:
        fail(f"{path}: header feature '{feature}' does not match package name '{expected_feature}'")
    if facet != "intent":
        fail(f"{path}: package entrypoint facet must be 'intent', got '{facet}'")


def validate_includes(entry_path: Path, expected_feature: str, expected_version: str) -> None:
    raw = entry_path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    include_entries: list[tuple[str, str]] = []
    include_block_found = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if INCLUDES_START_RE.match(line):
            if include_block_found:
                fail(f"{entry_path}: multiple INCLUDES blocks are not allowed")
            include_block_found = True
            seen_keys = set()
            i += 1

            while i < len(lines) and not INCLUDES_END_RE.match(lines[i]):
                current = lines[i]
                if not current.strip():
                    i += 1
                    continue
                m = INCLUDES_ENTRY_RE.match(current)
                if not m:
                    fail(
                        f"{entry_path}: malformed INCLUDES entry '{current.strip()}' "
                        "(expected: key: \"path.intent\")"
                    )
                include_facet, rel = m.groups()
                if include_facet in seen_keys:
                    fail(f"{entry_path}: duplicate INCLUDES key '{include_facet}'")
                seen_keys.add(include_facet)
                include_entries.append((include_facet, rel))
                i += 1

            if i >= len(lines):
                fail(f"{entry_path}: unterminated INCLUDES block")

        elif re.match(r"^\s*INCLUDES\b", line):
            fail(f"{entry_path}: malformed INCLUDES declaration (expected: INCLUDES {{)")

        i += 1

    for include_facet, rel in include_entries:
        rel_path = Path(rel)
        if rel_path.is_absolute():
            fail(f"{entry_path}: INCLUDES path must be relative, got '{rel}'")
        if not rel.endswith(".intent"):
            fail(f"{entry_path}: INCLUDES path must end with .intent, got '{rel}'")
        if ".." in rel_path.parts:
            fail(f"{entry_path}: INCLUDES path must not contain parent traversal, got '{rel}'")
        target = entry_path.parent / rel
        if not target.exists():
            fail(f"{entry_path}: includes missing file '{rel}'")
        feature, facet, version = validate_source_file(
            target,
            package_root=REGISTRY_PACKAGES / expected_feature,
            expected_feature=expected_feature,
            expected_version=expected_version,
        )
        if facet != include_facet:
            fail(f"{entry_path}: include '{rel}' facet '{facet}' does not match key '{include_facet}'")


def validate_no_stale_manifests() -> None:
    stale = []
    for pkg_dir in sorted([p for p in REGISTRY_PACKAGES.iterdir() if p.is_dir()]):
        for name in ("package.json", "manifest.ail", "manifest.intent"):
            if (pkg_dir / name).exists():
                stale.append(str(pkg_dir / name))
    if stale:
        fail(f"stale package manifests are not allowed: {', '.join(stale)}")


def validate_index_and_packages() -> int:
    if not REGISTRY_INDEX.exists():
        fail(f"missing registry index: {REGISTRY_INDEX}")
    try:
        index = json.loads(REGISTRY_INDEX.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{REGISTRY_INDEX}: invalid JSON ({exc})")

    if not isinstance(index, dict):
        fail(f"{REGISTRY_INDEX}: root must be an object")
    if "version" not in index:
        fail(f"{REGISTRY_INDEX}: missing required key 'version'")
    if "packages" not in index:
        fail(f"{REGISTRY_INDEX}: missing required key 'packages'")
    if not isinstance(index["packages"], list) or not index["packages"]:
        fail(f"{REGISTRY_INDEX}: 'packages' must be a non-empty array")

    package_dirs = sorted([p for p in REGISTRY_PACKAGES.iterdir() if p.is_dir()])
    package_names = {p.name for p in package_dirs}
    indexed_names = set()

    for idx, pkg in enumerate(index["packages"], start=1):
        if not isinstance(pkg, dict):
            fail(f"{REGISTRY_INDEX}: package at index {idx} must be an object")
        for key in ("name", "version", "entry"):
            if key not in pkg:
                fail(f"{REGISTRY_INDEX}: package at index {idx} missing '{key}'")
        name = pkg["name"]
        version = pkg["version"]
        entry = pkg["entry"]
        if not isinstance(name, str) or not FEATURE_RE.match(name):
            fail(f"{REGISTRY_INDEX}: invalid package name '{name}'")
        if name in indexed_names:
            fail(f"{REGISTRY_INDEX}: duplicate package name '{name}'")
        indexed_names.add(name)
        if not isinstance(version, str) or not VERSION_RE.match(version):
            fail(f"{REGISTRY_INDEX}: package '{name}' has invalid version '{version}'")
        if not isinstance(entry, str) or not entry.endswith(".intent"):
            fail(f"{REGISTRY_INDEX}: package '{name}' entry must be a .intent path")
        entry_path = ROOT / entry
        if not entry_path.exists():
            fail(f"{REGISTRY_INDEX}: package '{name}' entry does not exist: {entry}")
        expected_prefix = f"registry/packages/{name}/"
        if not entry.startswith(expected_prefix):
            fail(f"{REGISTRY_INDEX}: package '{name}' entry must be under '{expected_prefix}'")
        validate_entry_file(entry_path, expected_feature=name, expected_version=version)
        validate_includes(entry_path, expected_feature=name, expected_version=version)
        intent_entry_files = []
        seen_identities: dict[tuple[str, str], Path] = {}
        for source in sorted((REGISTRY_PACKAGES / name).rglob("*.intent")):
            source_feature, source_facet, _source_version = validate_source_file(
                source,
                package_root=REGISTRY_PACKAGES / name,
                expected_feature=name,
                expected_version=version,
            )
            identity = (source_feature, source_facet)
            if identity in seen_identities:
                fail(
                    f"{REGISTRY_PACKAGES / name}: duplicate source identity {source_feature}#{source_facet} "
                    f"found in '{seen_identities[identity].relative_to(REGISTRY_PACKAGES / name)}' and "
                    f"'{source.relative_to(REGISTRY_PACKAGES / name)}'"
                )
            seen_identities[identity] = source
            if source_facet == "intent":
                intent_entry_files.append(source)
        if len(intent_entry_files) != 1:
            fail(f"{REGISTRY_PACKAGES / name}: must contain exactly one #intent source file")
        if intent_entry_files[0].resolve() != entry_path.resolve():
            fail(
                f"{REGISTRY_INDEX}: package '{name}' entry must match intent file "
                f"'{intent_entry_files[0].name}'"
            )

    if indexed_names != package_names:
        missing_in_index = sorted(package_names - indexed_names)
        missing_on_disk = sorted(indexed_names - package_names)
        details = []
        if missing_in_index:
            details.append(f"missing in index: {missing_in_index}")
        if missing_on_disk:
            details.append(f"missing on disk: {missing_on_disk}")
        fail(f"{REGISTRY_INDEX}: package/index mismatch ({'; '.join(details)})")
    return len(index["packages"])


def main() -> None:
    if not REGISTRY_PACKAGES.exists():
        fail(f"missing directory: {REGISTRY_PACKAGES}")

    if not any(p.is_dir() for p in REGISTRY_PACKAGES.iterdir()):
        fail("registry/packages must contain at least one package directory")

    validate_no_stale_manifests()
    count = validate_index_and_packages()
    print(f"[OK] Validated {count} package(s)")


if __name__ == "__main__":
    main()
