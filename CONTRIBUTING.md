# Contributing

## Feature Registry Publishing

Community feature packages are published via pull requests to `registry/packages`.

1. Create a package directory: `registry/packages/<feature>/`.
2. Add `package.json` with required keys:
   - `name`
   - `version` (`x.y`)
   - `summary`
   - `files` (array of `.ail` file paths)
3. Add package AIL files at package root.
4. Open a pull request.

CI validates package integrity and AIL header conventions.

## Spec Changes

Protocol changes should update:

- `specification.md` (canonical language spec)
- `README.md` (landing summary, if needed)

If a spec change affects registry rules, update `scripts/validate_registry.py`.
