# AIM Feature Registry

This directory is the publish surface for community AIM feature packages.

## Package Layout

Each package lives in:

- `registry/packages/<feature>/`

Each package must contain:

1. Exactly one intent entry file: `<feature>.intent`
2. Optional additional facet files referenced by the intent file

## `registry/index.json` Schema

Required fields:

- `version`: index schema version
- `packages`: array of package objects

Each package object requires:

- `name`: feature namespace (lowercase, dot-separated segments; single-segment allowed)
- `version`: `x.y` matching entry file header
- `entry`: relative path to canonical intent file

## Pull Request Publishing Flow

1. Fork and create a branch.
2. Add or update package files in `registry/packages/<feature>/`.
3. Update `registry/index.json` with package `name`, `version`, and `entry`.
4. Open a PR.
5. CI runs `scripts/validate_registry.py`.
6. Maintainers review and merge.

Merged PRs are the publishing mechanism.

## Consumption Model

Consumers fetch package `entry` from this registry, resolve related sources, and materialize files into local project `/ail` (and `/ail/mappings` when applicable) before synthesis.

## Validation Rules

CI enforces:

- index schema validity and non-empty package list
- package/index consistency (one index record per package directory)
- `entry` exists and points to `.intent`
- entry header matches `name`, `intent` facet, and `version`
- exactly one `*.intent` file per package directory
- optional `INCLUDES` targets exist and match feature/facet/version
- stale manifest files (`package.json`, `manifest.intent`) are rejected
- legacy metadata tokens are rejected

## Notes

- Keep package changes focused per PR.
- Include release notes in the PR description for version bumps.
