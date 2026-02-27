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
- optional precision detail: `schema`, `flow`, `contract`, `persona`, `view` authored inline or in separate files

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
^AIM:\s+([a-z0-9]+(?:\.[a-z0-9]+)*)#(intent|schema|flow|contract|persona|view|mapping)@([0-9]+\.[0-9]+)$
```

Rules:

- `<feature>` must be lowercase namespace segments separated by dots (single segment allowed).
- `<facet>` must be one of:
  - `intent`
  - `schema`
  - `flow`
  - `contract`
  - `persona`
  - `view`
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
  game.snake.view.intent
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

- `TESTS`

### 4.1 Minimal Template

```ail
AIM: demo.todo#intent@1.4

INTENT TodoFeature {
  SUMMARY: "A simple personal todo tracker."
  REQUIREMENTS {
    - "User can add, complete, and delete todos."
  }
}
```

### 4.2 Extended Template

```ail
AIM: game.snake#intent@1.4

INTENT SnakeGame {
  SUMMARY: "A single-player snake game with persistent top scores."
  REQUIREMENTS {
    - "Movement is tick-based."
    - "Wall and self collision end the run."
  }

  TESTS {
    - "Describe acceptance scenarios."
  }
}
```

### 4.3 Embedded Facet Blocks In Intent

Inside `INTENT <Name> { ... }`, authors may include optional embedded facet blocks using the same Relaxed AIM DSL syntax as standalone facet files.

- `SCHEMA`
- `FLOW`
- `CONTRACT`
- `PERSONA`
- `VIEW`

These embedded blocks are additive and intended for lightweight one-file authoring.
Allowed embedded facet keys are uppercase `SCHEMA`, `FLOW`, `CONTRACT`, `PERSONA`, and `VIEW` only.
All embedded facet content follows the same brace-based rules: `{}` for hierarchy (with whitespace/newlines between braces ignored by the parser), no commas, quoted natural-language strings, and hyphen-led list items.

Minimal embedded example:

```ail
AIM: weather#intent@1.4

INTENT WeatherLookup {
  SUMMARY: "Get current weather by city."
  REQUIREMENTS {
    - "User can enter a city and fetch current weather."
  }

  SCHEMA WeatherSnapshot {
    ATTRIBUTES {
      city: string required
      temperatureC: number required
    }
  }
}
```

Mixed-source example:

```ail
AIM: weather#intent@1.4

INTENT WeatherLookup {
  SUMMARY: "Get current weather by city."
  REQUIREMENTS {
    - "User can fetch weather and retry on failure."
  }

  SCHEMA WeatherSnapshot {
    ATTRIBUTES {
      humidityPct: integer optional min(0) max(100)
    }
  }
}

SCHEMA WeatherSnapshot {
  SUMMARY: "Authoritative schema detail."
  REQUIREMENTS {
    - "Humidity is required."
  }

  ATTRIBUTES {
    humidityPct: integer required min(0) max(100)
  }
}
```

---

## 5. `INCLUDES` for Linked External Facets

Intent files may link external detail files using `INCLUDES`.

Canonical form:

```ail
INCLUDES {
  schema: "game.snake.schema.intent"
  flow: "game.snake.flow.intent"
  contract: "game.snake.contract.intent"
  persona: "game.snake.persona.intent"
  view: "game.snake.view.intent"
}
```

### 5.1 `INCLUDES` Validation

For each entry:

- key must be one of `schema|flow|contract|persona|view`
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
3. embedded facet DSL block in `INTENT` body (if present)
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

This repository includes a compact mixed-source hybrid-envelope example:

- intent envelope: `ail/game.snake.intent`
- inline facets inside the intent envelope:
  - `SCHEMA GameSession`
  - `SCHEMA ScoreEntry`
  - `FLOW AdvanceTick`
  - `PERSONA Player`
- linked external facets via `INCLUDES`:
  - `ail/game.snake.contract.intent`
  - `ail/game.snake.view.intent`

For this example, an AI synthesizer should:

1. parse `game.snake#intent@1.4`
2. parse `INCLUDES` links
3. parse embedded `SCHEMA`, `FLOW`, and `PERSONA` blocks in the intent body
4. load linked external `CONTRACT` and `VIEW` facets
5. treat linked external facets as authority for those facet types
6. use `INTENT` and optional `TESTS` as feature-level narrative and acceptance guidance

---

## 7. Optional Detail Facets

Detail facets are optional precision overlays.
When authored inline inside an intent envelope, facet constructs use the same grammar and properties as standalone facet files.

### 7.0 Source Authority And Precedence

For each facet (`schema|flow|contract|persona|view`), effective source is:

| Priority | Source | Notes |
| --- | --- | --- |
| 1 | External linked facet (`INCLUDES`) | Highest authority |
| 2 | Top-level inline facet block (`SCHEMA Name {}` etc.) | Used when no external source |
| 3 | Embedded DSL block inside `INTENT` | Lightweight fallback |
| 4 | Absent facet | Allowed |

If multiple sources exist for the same facet, the higher-priority source wins and lower-priority content is ignored for synthesis with informational diagnostics.

### 7.1 Schema Facet

Purpose: data at rest.
Syntax: `SCHEMA <Name> { ... }` blocks with nested brace-delimited sections and newline-separated entries (no commas).

Common blocks:

- `SCHEMA`
- `SUMMARY`
- `ATTRIBUTES`
- `RELATIONSHIPS`
- `CONSTRAINTS`
- `IMMUTABLE`

Common modifiers:

- `required`, `optional`, `unique`, `generated`, `immutable`
- `default(...)`, `min(...)`, `max(...)`, `pattern(...)`
- `enum(...)`, `ref(...)`

### 7.2 Flow Facet

Purpose: Internal mechanics and step-by-step orchestration. Flows define *how* an operation is executed under the hood, detailing the sequence of internal logic, branching, external API calls, and error handling.
Syntax: `FLOW <Name> { ... }` blocks with nested brace-delimited sections and newline-separated entries (no commas).

Common blocks:

- `FLOW`
- `SUMMARY`
- `TRIGGER`
- `STEPS`
- `ON_ERROR`

Common logic keywords for STEPS:

- `EVALUATE`, `CALL`, `ITERATE`, `BRANCH`, `AWAIT`, `TRANSITION`

```ail
FLOW ExecuteTodoCompletion {
  SUMMARY: "Orchestrates the database update and event publishing for completing a todo."

  TRIGGER {
    - "Invoked by CompleteTodo CONTRACT"
  }

  STEPS {
    - "CALL Storage.BeginTransaction"
    - "CALL Storage.FetchById(todoId)"
    - "EVALUATE if already completed, early return"
    - "UPDATE record in memory with status='COMPLETED'"
    - "CALL Storage.Save(record)"
    - "CALL EventBus.Publish('TodoCompleted', record)"
    - "CALL Storage.CommitTransaction"
  }

  ON_ERROR {
    - "CALL Storage.RollbackTransaction"
    - "RETHROW error to CONTRACT layer"
  }
}
```

### 7.3 Contract Facet

Purpose: Execution guardrails and guaranteed outcomes (Design by Contract). Contracts define what an operation must enforce and guarantee, rather than how it achieves it line-by-line.

Syntax: CONTRACT <Name> { ... } blocks with nested brace-delimited sections and newline-separated entries (no commas).

Common blocks: CONTRACT, SUMMARY, INPUT, AUTHZ, EXPECTS (pre-conditions), ENSURES (post-conditions/mutations), RETURNS.

Common logic keywords for ENSURES: PERSISTS, UPDATES, DELETES, EMITS, CALLS.

```ail
CONTRACT CompleteTodo {
  SUMMARY: "Safely marks an active todo as complete."

  INPUT {
    todoId: string required
  }

  AUTHZ {
    - "User must be actively authenticated"
    - "User must be the owner of the Todo record"
  }

  EXPECTS {
    - "Todo record must exist in the database"
    - "Todo.status must currently be 'PENDING'"
  }

  ENSURES {
    - UPDATES "Todo.status to 'COMPLETED'"
    - EMITS "TodoCompletedEvent to the analytics stream"
  }

  RETURNS {
    - "The updated Todo entity"
  }
}
```

### 7.4 Persona Facet

Purpose: User-visible actor definition, role constraints, and interface access mapping. Personas define *who* interacts with the system and which shared `VIEW`s they are permitted to load.

Syntax: `PERSONA <Name> { ... }` blocks as top-level constructs, using nested brace-delimited sections and newline-separated entries (no commas).

Common `PERSONA` blocks:
- `PERSONA`: The user archetype or system actor.
- `SUMMARY`: The human-readable summary of the persona's goals.
- `ROLE`: The authorization baseline (maps to `AUTHZ` in Contracts).
- `ACCESS`: The specific `VIEW` blocks this persona is permitted to load.

```ail
PERSONA StandardUser {
  ROLE {
    - "user:standard"
  }
  ACCESS {
    - VIEW TodoDashboard
  }
}

PERSONA AdminUser {
  ROLE {
    - "user:admin"
  }
  ACCESS {
    - VIEW TodoDashboard
    - VIEW SystemSettings
  }
}
```

### 7.5 View Facet

Purpose: Shared interface surfaces and interaction mapping. Views define *what* a user can see and do on a screen, page, or UI state, and may be reused across multiple Personas without duplication.

Syntax: `VIEW <Name> { ... }` blocks as top-level constructs, using nested brace-delimited sections and newline-separated entries (no commas).

Common `VIEW` blocks:
- `VIEW`: A distinct screen, page, or UI state shared across permitted Personas.
- `SUMMARY`: The human-readable summary of the view.
- `DISPLAY`: The read-only data requirements (supports natural language conditionals, e.g., "If Admin, show X").
- `ACTIONS`: The interactive elements available in the view (triggers mapping directly to Contracts).

```ail
VIEW TodoDashboard {
  SUMMARY: "The primary unified dashboard for managing tasks."
  
  DISPLAY {
    - "A list of Todo items filtered by status='PENDING'"
    - "A progress indicator showing completed vs total daily tasks"
    - "If AdminUser, show the 'Assigned To' column"
  }
  
  ACTIONS {
    - "Clicking 'Add Task' -> CALL CreateTodo"
    - "Tapping checkbox -> CALL CompleteTodo"
    - "Clicking 'Reassign' -> CALL ReassignTodo"
  }
}
```

### 7.6 View And Persona Summary Rule

`VIEW` is a top-level shared UI-surface construct and must include `SUMMARY`.

`PERSONA` is a separate top-level access/role construct. It may include `SUMMARY`, but `ROLE` + `ACCESS` alone are sufficient when the persona acts only as a role/access declaration.

---

## 8. Dependencies, Requirements, and Mapping

### 8.1 Dependencies

`DEPENDENCIES` may appear in intent files and/or detail files.

```ail
DEPENDENCIES {
  IMPORT {
    company.storage.Contract AS Storage
  }
  REQUIRES {
    Identity AS AssigneeUsers
  }
}
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
`TARGET` identifies the destination capability provider, whether it is another AIM feature namespace or an external implementation surface.

```ail
MAP AssigneeUsers {
  TARGET: "company.identity"
  OPERATION_MAP {
    - "AssigneeUsers.ResolveUser -> Identity.ResolveUser"
  }
}
```

or

```ail
MAP AssigneeUsers {
  TARGET: "ExistingCode.IdentityGateway"
  OPERATION_MAP {
    - "AssigneeUsers.ResolveUser -> ExistingCode.IdentityGateway.resolveUser"
  }
}
```

Unresolved required aliases remain hard errors.

---

## 9. Binding Rule and Traceability

When relevant detail facets exist, the chain is:

```text
Persona -> View -> Contract -> Flow / Schema
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

5. Embedded facet block violations
- invalid embedded facet key in `INTENT` body
- malformed embedded block syntax (including mismatched curly braces) when that block is selected as effective facet source

6. Unresolved required references
- unresolved `REQUIRES` alias in `CALL Alias.Operation`
- unresolved `REQUIRES` alias in `ref(Alias.Type)`
- missing provider/mapping for required aliases

### 11.2 Informational Diagnostics

- missing optional `TESTS`
- no detail facets provided
- inline facet overridden by external facet
- embedded facet block overridden by top-level or external facet
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
10. Parse optional embedded facet DSL blocks in intent bodies.
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
2. Valid header parse: `AIM: juice.games.snake#view@2.1`.
3. Invalid feature namespace: `AIM: Snake-App#schema@2.1` -> hard error.
4. Invalid facet: `AIM: juice.games.snake#data@2.1` -> hard error.
5. Invalid version: `AIM: juice.games.snake#schema@2.1.0` -> hard error.
6. Filename/header mismatch -> hard error.
7. Legacy metadata token in source -> hard error.
8. Intent-only feature parses and synthesizes with reduced-fidelity informational note.
9. Valid `INCLUDES` resolves linked facets.
10. Valid `INCLUDES` resolves linked view facet.
11. Included file missing -> hard error.
12. Included file facet mismatch -> hard error.
13. Inline + external same facet -> informational override note, external used.
14. Parse success: intent file with embedded `SCHEMA <Name> { ... }` block only.
15. Parse success: intent file with embedded `SCHEMA/FLOW/CONTRACT/PERSONA/VIEW` blocks only.
16. Parse success: intent file with embedded DSL block + top-level blocks + `INCLUDES`.
17. Precedence: linked external overrides top-level and embedded DSL blocks.
18. Precedence: top-level overrides embedded DSL blocks when no external exists.
19. Hard failure: invalid embedded facet key (`DATA:`).
20. Hard failure: malformed embedded block syntax or mismatched curly braces when selected as effective source.
21. Informational note: embedded DSL block overridden by top-level or external facet.
22. Existing separate facet projects remain valid when linked via intent `INCLUDES`.
23. Unresolved `REQUIRES` still hard-fails.
24. Registry package entry resolves to existing `#intent` source matching index `name` and `version`.
25. Remote package fetch materialized into local `/ail` enables subsequent local-only rebuild.

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
