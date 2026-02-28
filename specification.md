# Application Intent Model (AIM) v1.5

Application Intent Model (AIM) is an intent-first specification language for humans and AI agents. It captures product behavior in a form that is readable enough for product/design discussion and structured enough for deterministic synthesis.

AIM supports progressive precision:

- start with a single intent file
- add detailed facets only when you need stronger guarantees

This allows fast authoring for simple features and high-fidelity synthesis for complex features.

---

## 1. Core Model

A feature is identified by a namespace such as `company.subsystem` (for example `game.snake`, `juice.tasks`).

In v1.5, each feature uses a **hybrid intent envelope** model:

- required baseline: one intent entry file (`<feature>.intent`)
- optional precision detail: `schema`, `flow`, `contract`, `persona`, `view`, `event` authored inline or in separate files

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
^AIM:\s+([a-z0-9]+(?:\.[a-z0-9]+)*)#(intent|schema|flow|contract|persona|view|event|mapping)@([0-9]+\.[0-9]+)$
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
  - `event`
  - `mapping`
- `<version>` is short SemVer form `x.y`.

### 2.2 Filename And Path Linkage

Source identity may use either flat or nested layout, but physical path must match header identity:

- flat feature file: `<feature>.<facet>.intent`
- nested feature file: `/aim/<namespace segments>/<facet>.intent`
- flat mapping file: `/aim/mappings/<feature>.mapping.intent`
- nested mapping file: `/aim/mappings/<namespace segments>/mapping.intent`
- header: `AIM: <feature>#<facet>@<x.y>`

Examples:

- `game.snake.schema.intent` must declare `AIM: game.snake#schema@1.5`.
- `/aim/game/snake/schema.intent` must declare `AIM: game.snake#schema@1.5`.
- `/aim/game/snake/event.intent` must declare `AIM: game.snake#event@1.5`.
- `/aim/mappings/game/snake/mapping.intent` must declare `AIM: game.snake#mapping@1.5`.

Hard error example:

- `/aim/company/hr/invoice/schema.intent` with `AIM: company.billing.invoice#schema@1.5`.

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

Source discovery recursively scans folders under `/aim`.

- discover feature sources recursively under `/aim`
- do not include `/aim/mappings` in feature source discovery
- discover mapping sources recursively under `/aim/mappings`
- derive expected namespace and facet from physical path
- treat the header as the ultimate source of truth, but hard-fail when path-derived identity does not match it

Typical layout:

```text
/aim/
  game.snake.intent
  game.snake.schema.intent
  game.snake.contract.intent
  game.snake.event.intent
  game/
    snake/
      intent.intent
      schema.intent
      contract.intent
      event.intent
  mappings/
    game.snake.mapping.intent
    game/
      snake/
        mapping.intent
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
- package directory must contain exactly one `#intent` source file across recursive scan
- stale per-package manifests (`package.json`, `manifest.intent`) are invalid

### 3.2 Local Materialization Rule

Even when sources are fetched remotely, synthesis must run against local files in project `/aim`.

Required behavior:

1. fetch selected package entry and related facet sources
2. materialize them into local `/aim` before synthesis using either flat or nested layout
3. materialize mapping sources into local `/aim/mappings` when applicable using either flat or nested layout
4. synthesize from local `/aim` so users can edit and rebuild without refetching

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
AIM: demo.todo#intent@1.5

INTENT TodoFeature {
  SUMMARY: "A simple personal todo tracker."
  REQUIREMENTS {
    - "User can add, complete, and delete todos."
  }
}
```

### 4.2 Extended Template

```ail
AIM: game.snake#intent@1.5

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
- `EVENT`

These embedded blocks are additive and intended for lightweight one-file authoring.
Allowed embedded facet keys are uppercase `SCHEMA`, `FLOW`, `CONTRACT`, `PERSONA`, `VIEW`, and `EVENT` only.
All embedded facet content follows the same brace-based rules: `{}` for hierarchy (with whitespace/newlines between braces ignored by the parser), no commas, quoted natural-language strings, and hyphen-led list items.

Minimal embedded example:

```ail
AIM: weather#intent@1.5

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
AIM: weather#intent@1.5

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
  event: "game.snake.event.intent"
}
```

### 5.1 `INCLUDES` Validation

For each entry:

- key must be one of `schema|flow|contract|persona|view|event`
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

For each facet (`schema|flow|contract|persona|view|event`), effective source is:

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

### 7.6 Event Facet

Purpose: Defines asynchronous payloads, state-change broadcasts, and routing rules.

Syntax: `EVENT <Name> { ... }` blocks as top-level constructs, using nested brace-delimited sections and newline-separated entries (no commas).

Common `EVENT` blocks:
- `EVENT`: The named asynchronous message or broadcast.
- `SUMMARY`: The human-readable summary of the event's purpose.
- `PAYLOAD`: The data shape carried by the event.
- `EMITTED_BY`: Traceability back to the `CONTRACT` that guarantees emission.
- `ROUTING`: Delivery and subscriber declarations.

```ail
AIM: shopping.checkout#event@1.5

EVENT OrderConfirmed {
  SUMMARY: "Broadcasted to the enterprise service bus when a user successfully checks out."

  EMITTED_BY {
    - "CONTRACT PlaceOrder ENSURES [post:3]"
  }

  PAYLOAD {
    eventId: uuid generated
    timestamp: datetime generated
    orderId: string required
    totalAmount: number required
    customerId: string required
  }

  ROUTING {
    - "TOPIC: enterprise.orders.confirmed"
    - "SUBSCRIBERS: EmailService, AnalyticsEngine"
  }
}
```

### 7.7 Summary Rule

`SCHEMA`, `FLOW`, `CONTRACT`, `VIEW`, and `EVENT` are top-level detail constructs and must include `SUMMARY`.

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

Mappings are declared in `/aim/mappings` files with `facet=mapping`.
`TARGET` identifies the destination capability provider, whether it is another AIM feature namespace or an external implementation surface.

Accepted mapping source paths:

- flat: `/aim/mappings/company.billing.invoice.mapping.intent`
- nested: `/aim/mappings/company/billing/invoice/mapping.intent`

Both forms must declare `AIM: company.billing.invoice#mapping@1.5`.

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
Persona -> View -> Contract -> Flow / Schema / Event
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
- filename/path/header mismatch
- malformed construct syntax
- path-derived feature does not match header feature
- path-derived facet does not match header facet
- duplicate source identity across flat/nested layouts for the same feature and facet
- invalid nested source path shape

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
4. Materialize fetched sources into local `/aim` and mappings into `/aim/mappings`.
5. Discover feature source `.intent` files recursively under local `/aim`, excluding `/aim/mappings`.
6. Discover mapping source `.intent` files recursively under local `/aim/mappings`.
7. Derive expected feature/facet identity from each source path.
8. Parse and validate header declarations.
9. Hard-fail on filename/path/header mismatch or duplicate source identity.
10. Group files by feature.
11. Parse intent envelopes.
12. Resolve `INCLUDES` links.
13. Parse optional embedded facet DSL blocks in intent bodies.
14. Merge external/inline/embedded facets by resolution order and authority rules.
15. Parse dependencies/requirements.
16. Load mappings from local `/aim/mappings` when present.
17. Resolve required aliases.
18. Determine synthesis tier.
19. Synthesize artifacts with tier-appropriate precision.
20. Apply traceability checks where applicable.

---

## 13. Conformance Scenarios

1. Valid header parse: `AIM: juice.games.snake#schema@2.1`.
2. Valid header parse: `AIM: juice.games.snake#view@2.1`.
3. Valid header parse: `AIM: shopping.checkout#event@1.5`.
4. Valid flat source path parse: `/aim/company.billing.invoice.schema.intent` -> `AIM: company.billing.invoice#schema@1.5`.
5. Valid nested source path parse: `/aim/company/billing/invoice/schema.intent` -> `AIM: company.billing.invoice#schema@1.5`.
6. Valid nested source path parse: `/aim/company/billing/invoice/event.intent` -> `AIM: company.billing.invoice#event@1.5`.
7. Valid nested mapping path parse: `/aim/mappings/company/billing/invoice/mapping.intent` -> `AIM: company.billing.invoice#mapping@1.5`.
8. Invalid feature namespace: `AIM: Snake-App#schema@2.1` -> hard error.
9. Invalid facet: `AIM: juice.games.snake#data@2.1` -> hard error.
10. Invalid version: `AIM: juice.games.snake#schema@2.1.0` -> hard error.
11. Filename/path/header mismatch -> hard error.
12. Nested path/header feature mismatch -> hard error.
13. Nested path/header facet mismatch -> hard error.
14. Duplicate flat + nested source for same feature/facet -> hard error.
15. Legacy metadata token in source -> hard error.
16. Intent-only feature parses and synthesizes with reduced-fidelity informational note.
17. Valid `INCLUDES` resolves linked facets.
18. Valid `INCLUDES` resolves linked view facet.
19. Valid `INCLUDES` resolves linked event facet.
20. Included file missing -> hard error.
21. Included file facet mismatch -> hard error.
22. Inline + external same facet -> informational override note, external used.
23. Parse success: intent file with embedded `SCHEMA <Name> { ... }` block only.
24. Parse success: intent file with embedded `SCHEMA/FLOW/CONTRACT/PERSONA/VIEW/EVENT` blocks only.
25. Parse success: intent file with embedded DSL block + top-level blocks + `INCLUDES`.
26. Precedence: linked external overrides top-level and embedded DSL blocks.
27. Precedence: top-level overrides embedded DSL blocks when no external exists.
28. Hard failure: invalid embedded facet key (`DATA:`).
29. Hard failure: malformed embedded block syntax or mismatched curly braces when selected as effective source.
30. Informational note: embedded DSL block overridden by top-level or external facet.
31. Existing separate facet projects remain valid when linked via intent `INCLUDES`.
32. Unresolved `REQUIRES` still hard-fails.
33. Registry package entry resolves to existing `#intent` source matching index `name` and `version`.
34. Remote package fetch materialized into local `/aim` enables subsequent local-only rebuild.

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
