# Application Intent Model (AIM) v1.4

Application Intent Model (AIM) is an intent-first specification language for humans and AI agents. It captures product behavior in a form that is readable enough for product/design discussion and structured enough for deterministic synthesis.

AIM supports progressive precision:

- start with a single intent file
- add detailed facets only when you need stronger guarantees

This allows fast authoring for simple features and high-fidelity synthesis for complex features.

---

## 1. Core Model

A feature is identified by a namespace such as `company.subsystem` (for example `game.snake`, `juice.tasks`).

In v1.4, each feature uses a **hybrid intent envelope** model:

- required baseline: one intent entry file (`<feature>.intent`)
- optional precision detail: `schema`, `flow`, `contract`, `persona` authored inline or in separate files

No detail facet is required for a feature to be valid.

---

## 2. Canonical Header Declaration

Every source `.intent` file must start with one declaration line:

```ail
AIM: <feature>#<facet>@<x.y>
```

Example:

```ail
AIM: juice.games.snake#schema@2.1
```

### 2.1 Grammar

```regex
^AIM:\s+([a-z0-9]+(?:\.[a-z0-9]+)*)#(intent|schema|flow|contract|persona|mapping)@([0-9]+\.[0-9]+)$
```

Rules:

- `<feature>` must be lowercase namespace segments separated by dots (single segment allowed).
- `<facet>` must be one of:
  - `intent`
  - `schema`
  - `flow`
  - `contract`
  - `persona`
  - `mapping`
- `<version>` is short SemVer form `x.y`.

### 2.2 Filename Linkage

Basename must match header identity:

- filename: `<feature>.<facet>.intent`
- header: `AIM: <feature>#<facet>@<x.y>`

Example:

- `game.snake.schema.intent` must declare `AIM: game.snake#schema@1.4`.

### 2.3 Compatibility Policy

Migration is immediate:

- legacy block metadata is invalid in source files
- only the one-line `AIM: ...` preamble is valid

Legacy tokens treated as parse violations:

- `:::AIL_METADATA`
- `FEATURE:`
- `FACET:`
- `VERSION:`

---

## 3. Source Layout

Source discovery uses `/ail` root files only.

- include files directly under `/ail`
- do not include `/ail/mappings` in feature source discovery

Typical layout:

```text
/ail/
  game.snake.intent
  game.snake.schema.intent
  game.snake.flow.intent
  game.snake.contract.intent
  game.snake.persona.intent
  mappings/
    game.snake.mapping.intent
```

### 3.1 Registry Package Catalog

Remote package discovery is defined by `registry/index.json`.

Each package object must include:

- `name`
- `version`
- `entry` (path to canonical intent file)

Package validity rules:

- `entry` must exist and end with `.intent`
- `entry` header must match `AIM: <name>#intent@<version>`
- package directory must contain exactly one `*.intent`
- stale per-package manifests (`package.json`, `manifest.intent`) are invalid

### 3.2 Local Materialization Rule

Even when sources are fetched remotely, synthesis must run against local files in project `/ail`.

Required behavior:

1. fetch selected package entry and related facet sources
2. materialize them into local `/ail` before synthesis
3. materialize mapping sources into local `/ail/mappings` when applicable
4. synthesize from local `/ail` so users can edit and rebuild without refetching

---

## 4. Intent Envelope (`<feature>.intent`)

Intent file is the canonical feature entrypoint.

Hard minimum for validity:

- valid `AIM: ...` preamble with `facet=intent`
- one top-level named declaration: `INTENT <Name> { ... }`
- `SUMMARY` inside intent body (one sentence)
- `REQUIREMENTS` inside intent body (>= 1 item)

Recommended (non-blocking):

- `BEHAVIOR`
- `TESTS`

### 4.1 Minimal Template

```ail
AIM: demo.todo#intent@1.4

INTENT TodoFeature {
  SUMMARY: "A simple personal todo tracker."
  REQUIREMENTS:
    - User can add, complete, and delete todos.
}
```

### 4.2 Extended Template

```ail
AIM: game.snake#intent@1.4

INTENT SnakeGame {
  SUMMARY: "A single-player snake game with persistent top scores."
  REQUIREMENTS:
    - Movement is tick-based.
    - Wall and self collision end the run.
}

BEHAVIOR:
  - Describe loop and transitions.

TESTS:
  - Describe acceptance scenarios.
```

### 4.3 Embedded Facet Payloads In Intent

Inside `INTENT <Name> { ... }`, authors may include optional raw YAML payload properties:

- `SCHEMA: |`
- `FLOW: |`
- `CONTRACT: |`
- `PERSONA: |`

These payloads are additive and intended for lightweight one-file authoring.
Allowed embedded facet keys are uppercase `SCHEMA`, `FLOW`, `CONTRACT`, and `PERSONA` only.

Minimal embedded example:

```ail
AIM: weather#intent@1.4

INTENT WeatherLookup {
  SUMMARY: "Get current weather by city."
  REQUIREMENTS:
    - User can enter a city and fetch current weather.

  SCHEMA: |
    entities:
      - name: WeatherSnapshot
        fields:
          - name: city
            type: string
          - name: temperatureC
            type: number
}
```

Mixed-source example:

```ail
AIM: weather#intent@1.4

INTENT WeatherLookup {
  SUMMARY: "Get current weather by city."
  REQUIREMENTS:
    - User can fetch weather and retry on failure.

  SCHEMA: |
    entities:
      - name: WeatherSnapshot
        fields:
          - name: humidityPct
            required: false
}

SCHEMA WeatherSnapshot {
  INTENT:
    SUMMARY: "Authoritative schema detail."
    REQUIREMENTS:
      - Humidity is required.

  ATTRIBUTES:
    humidityPct: integer required min(0) max(100)
}
```

---

## 5. `INCLUDES` for Linked External Facets

Intent files may link external detail files using `INCLUDES`.

Canonical form:

```ail
INCLUDES:
  - schema: game.snake.schema.intent
  - flow: game.snake.flow.intent
  - contract: game.snake.contract.intent
  - persona: game.snake.persona.intent
```

### 5.1 `INCLUDES` Validation

For each entry:

- key must be one of `schema|flow|contract|persona`
- value must be a relative `.intent` path
- target file must exist
- target file preamble must match:
  - same feature namespace
  - same facet as include key
  - same version family (`x.y`) as envelope version

### 5.2 Resolution Order

Effective facet source is resolved in this order:

1. external facet declared in `INCLUDES` (if present)
2. top-level inline facet block in intent file (if present)
3. embedded facet YAML payload in `INTENT` body (if present)
4. facet absent (allowed)

### 5.3 Authority Rule

If multiple definitions exist for the same facet:

- higher-precedence source is authoritative for synthesis detail
- emit informational diagnostics for overridden lower-precedence sources

### 5.4 Fallback Discovery

Default behavior: no fallback auto-discovery beyond explicit `INCLUDES`.

Implementations may add opt-in fallback behavior, but it is not part of core default semantics.

---

## 6. Worked Example (`game.snake`)

This repository includes a complete hybrid-envelope example:

- intent envelope: `ail/game.snake.intent`
- linked external facets via `INCLUDES`:
  - `ail/game.snake.schema.intent`
  - `ail/game.snake.flow.intent`
  - `ail/game.snake.contract.intent`
  - `ail/game.snake.persona.intent`

For this example, an AI synthesizer should:

1. parse `game.snake#intent@1.4`
2. parse `INCLUDES` links
3. load each linked external facet
4. treat linked facets as synthesis authority
5. use `INTENT`, `BEHAVIOR`, and `TESTS` as feature-level narrative and acceptance guidance

---

## 7. Optional Detail Facets

Detail facets are optional precision overlays.
When authored inline inside an intent envelope, facet constructs use the same grammar and properties as standalone facet files.

### 7.0 Source Authority And Precedence

For each facet (`schema|flow|contract|persona`), effective source is:

| Priority | Source | Notes |
| --- | --- | --- |
| 1 | External linked facet (`INCLUDES`) | Highest authority |
| 2 | Top-level inline facet block (`SCHEMA Name {}` etc.) | Used when no external source |
| 3 | Embedded YAML payload inside `INTENT` | Lightweight fallback |
| 4 | Absent facet | Allowed |

If multiple sources exist for the same facet, the higher-priority source wins and lower-priority content is ignored for synthesis with informational diagnostics.

### 7.1 Schema Facet

Purpose: data at rest.

Common blocks:

- `SCHEMA`
- `INTENT`
- `ATTRIBUTES`
- `RELATIONSHIPS`
- `CONSTRAINTS`
- `IMMUTABLE`

Common modifiers:

- `required`, `optional`, `unique`, `generated`, `immutable`
- `default(...)`, `min(...)`, `max(...)`, `pattern(...)`
- `enum(...)`, `ref(...)`

### 7.2 Flow Facet

Purpose: internal mechanisms.

Common blocks:

- `FLOW`
- `INTENT`
- `TRIGGER`
- `REQUIRES`
- `STEPS`

Flows are internal by design.

### 7.3 Contract Facet

Purpose: externally invokable operations.

Common blocks:

- `CONTRACT`
- `INTENT`
- `INPUT`
- `AUTHZ`
- `LOGIC`
- `INTERFACE`

Common logic keywords:

- `EXECUTE`, `PERSIST`, `SET`, `UPDATE`, `EMIT`, `REQUIRES`, `CALL`, `READ`, `RETURN`

### 7.4 Persona Facet

Purpose: user-visible experience.

Common blocks:

- `PERSONA`
- `INTENT`
- `VIEW`
- `DISPLAY`
- `ACTIONS`
- `form.create` / `form.edit`

### 7.5 Detail Construct Intent Rule

All top-level detail constructs (`SCHEMA`, `FLOW`, `CONTRACT`, `PERSONA`) must include `INTENT`.

---

## 8. Dependencies, Requirements, and Mapping

### 8.1 Dependencies

`DEPENDENCIES` may appear in intent files and/or detail files.

```ail
DEPENDENCIES:
  IMPORT:
    - company.storage.Contract AS Storage
  REQUIRES:
    - Identity AS AssigneeUsers
```

- `IMPORT` references concrete provider surfaces.
- `REQUIRES` declares required capabilities.

### 8.2 Requirement Surfaces

For each required capability alias, define `REQUIREMENT` surface.

### 8.3 Distributed Declarations

If dependency declarations are spread across files:

- resolve by union
- conflicting declarations emit informational diagnostic
- prefer detail-facet-local declarations for synthesis behavior

### 8.4 Mapping Files

Mappings are declared in `/ail/mappings` files with `facet=mapping`.

```ail
AIM: company.subsystem#mapping@1.4

MAP AssigneeUsers {
  TO FEATURE: company.identity
  OPERATION_MAP:
    - AssigneeUsers.ResolveUser -> Identity.ResolveUser
}
```

or

```ail
AIM: company.subsystem#mapping@1.4

MAP AssigneeUsers {
  TO EXTERNAL: ExistingCode.IdentityGateway
  OPERATION_MAP:
    - AssigneeUsers.ResolveUser -> ExistingCode.IdentityGateway.resolveUser
}
```

Unresolved required aliases remain hard errors.

---

## 9. Binding Rule and Traceability

When relevant detail facets exist, the chain is:

```text
Persona -> Contract -> Flow / Schema
```

`Schema` interaction includes reads and writes.

For intent-only features:

- skip strict chain enforcement
- emit reduced-fidelity informational note

---

## 10. Synthesis Tiers

- Tier 1: intent-only
- Tier 2: intent + partial facets
- Tier 3: intent + full facets

Tier impacts expected precision, generated structure depth, and strictness of traceability checks.

---

## 11. Diagnostics

### 11.1 Hard Errors

1. Header/parse violations
- missing preamble
- preamble not matching grammar
- filename/header mismatch
- malformed construct syntax

2. Legacy metadata tokens in source files
- `:::AIL_METADATA`
- `FEATURE:`
- `FACET:`
- `VERSION:`

3. Required intent minima missing
- missing `INTENT`
- missing intent name in `INTENT <Name> { ... }`
- missing `SUMMARY` in intent body
- missing `REQUIREMENTS` in intent body

4. `INCLUDES` violations
- invalid include key/value shape
- missing included file
- included file feature/facet/version-family mismatch

5. Embedded facet payload violations
- invalid embedded facet key in `INTENT` body
- malformed embedded YAML payload when that payload is selected as effective facet source

6. Unresolved required references
- unresolved `REQUIRES` alias in `CALL Alias.Operation`
- unresolved `REQUIRES` alias in `ref(Alias.Type)`
- missing provider/mapping for required aliases

### 11.2 Informational Diagnostics

- missing optional `BEHAVIOR` / `TESTS`
- no detail facets provided
- inline facet overridden by external facet
- embedded facet payload overridden by top-level or external facet
- unresolved `IMPORT` alias
- intent/detail narrative conflict (detail authority applied)

---

## 12. AI Synthesis Model

1. Load package catalog from `registry/index.json` (when using remote package selection).
2. Select package by `name` and fetch `entry` intent file.
3. Resolve related sources from `INCLUDES` and package-local references.
4. Materialize fetched sources into local `/ail` and mappings into `/ail/mappings`.
5. Discover source `.intent` files in local `/ail` root.
6. Parse and validate header declarations.
7. Group files by feature.
8. Parse intent envelopes.
9. Resolve `INCLUDES` links.
10. Parse optional embedded facet YAML payloads in intent bodies.
11. Merge external/inline/embedded facets by resolution order and authority rules.
12. Parse dependencies/requirements.
13. Load mappings from local `/ail/mappings` when present.
14. Resolve required aliases.
15. Determine synthesis tier.
16. Synthesize artifacts with tier-appropriate precision.
17. Apply traceability checks where applicable.

---

## 13. Conformance Scenarios

1. Valid header parse: `AIM: juice.games.snake#schema@2.1`.
2. Invalid feature namespace: `AIM: Snake-App#schema@2.1` -> hard error.
3. Invalid facet: `AIM: juice.games.snake#data@2.1` -> hard error.
4. Invalid version: `AIM: juice.games.snake#schema@2.1.0` -> hard error.
5. Filename/header mismatch -> hard error.
6. Legacy metadata token in source -> hard error.
7. Intent-only feature parses and synthesizes with reduced-fidelity informational note.
8. Valid `INCLUDES` resolves linked facets.
9. Included file missing -> hard error.
10. Included file facet mismatch -> hard error.
11. Inline + external same facet -> informational override note, external used.
12. Parse success: intent file with embedded `SCHEMA: |` only.
13. Parse success: intent file with embedded `SCHEMA/FLOW/CONTRACT/PERSONA` only.
14. Parse success: intent file with embedded payload + top-level blocks + `INCLUDES`.
15. Precedence: linked external overrides top-level and embedded payload.
16. Precedence: top-level overrides embedded payload when no external exists.
17. Hard failure: invalid embedded facet key (`DATA:`).
18. Hard failure: malformed embedded YAML when selected as effective source.
19. Informational note: embedded payload overridden by top-level or external facet.
20. Existing separate facet projects remain valid when linked via intent `INCLUDES`.
21. Unresolved `REQUIRES` still hard-fails.
22. Registry package entry resolves to existing `#intent` source matching index `name` and `version`.
23. Remote package fetch materialized into local `/ail` enables subsequent local-only rebuild.

---

## 14. Practical Guidance

Use intent-only when:

- feature is simple
- requirements are still evolving
- speed matters more than strict precision

Add detail facets when:

- schema compatibility must be explicit
- flow transitions must be deterministic
- contract surface must be stable
- persona traceability across roles is required

This is the intended AIM workflow: start light, add precision only where needed.
