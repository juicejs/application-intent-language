# AIL Feature Registry

This directory is the publish surface for community AIL feature packages.

## Package Layout

Each package lives in:

- `registry/packages/<feature>/`

Each package must contain:

1. `package.json`
2. One or more `.ail` source files at package root

## `package.json` Schema

Required fields:

- `name`: feature namespace (lowercase, dot-separated segments; single-segment allowed)
- `version`: `x.y`
- `summary`: short one-line description
- `files`: array of relative `.ail` file paths (for package entry files)

Example:

```json
{
  "name": "game.snake",
  "version": "1.3",
  "summary": "Single-player snake game with top-10 leaderboard",
  "files": [
    "game.snake.intent.ail",
    "game.snake.schema.ail",
    "game.snake.flow.ail",
    "game.snake.contract.ail",
    "game.snake.persona.ail"
  ]
}
```

## Pull Request Publishing Flow

1. Fork and create a branch.
2. Add or update a package in `registry/packages`.
3. Open a PR.
4. CI runs `scripts/validate_registry.py`.
5. Maintainers review and merge.

Merged PRs are the publishing mechanism.

## Validation Rules

CI enforces:

- package manifest required fields
- version format `x.y`
- package name and directory match
- listed files exist and end with `.ail`
- each file uses `AIL: <feature>#<facet>@<x.y>`
- legacy metadata tokens are rejected

## Notes

- Keep package changes focused per PR.
- Include release notes in the PR description for version bumps.
