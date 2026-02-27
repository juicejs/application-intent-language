# Generic AIM Synthesis Prompt

Use this prompt in a local AI coding session:

```md
Implement one AIM package in this local project.

Inputs:
- PACKAGE: <package-name>
- REF: <git-tag-or-commit>

Steps:
1. Fetch AIM spec:
   https://raw.githubusercontent.com/juicejs/application-intent-language/<REF>/specification.md
2. Fetch registry catalog:
   https://raw.githubusercontent.com/juicejs/application-intent-language/<REF>/registry/index.json
3. Resolve PACKAGE by `name` and fetch its `entry` file.
4. Resolve and fetch optional details from:
   - `INCLUDES` linked facets
   - top-level inline facet blocks
   - embedded facet payloads in `INTENT`
   using AIM precedence/diagnostics rules from the spec.
5. Materialize all fetched AIM sources into local:
   - `./aim/` for feature files
   - `./aim/mappings/` for mapping files (if present)
6. Generate production-ready code from local `./aim` in this repository's detected stack.
7. If any required reference is unresolved, stop and report precise gaps.

If network fetch is unavailable, use local fallback:
- ./specification.md
- ./registry/index.json
- package `entry` path from local index
- local `./aim` as synthesis source of truth
```
