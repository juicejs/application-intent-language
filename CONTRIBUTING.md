# Contributing

## Feature Registry Publishing

Community feature packages are published via pull requests to `registry/packages`.

1. Create a package directory: `registry/packages/<feature>/`.
2. Add exactly one package entry file: `<feature>.intent`.
3. Add optional facet files referenced by `INCLUDES` and/or inline intent payloads.
4. Open a pull request.
5. Update `registry/index.json` with `name`, `version`, and `entry`.

CI validates package integrity and AIM header conventions.

## Spec Changes

Protocol changes should update:

- `specification.md` (canonical language spec)
- `README.md` (landing summary, if needed)

If a spec change affects registry rules, update `scripts/validate_registry.py`.
