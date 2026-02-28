# Application Intent Model (AIM)

AIM is an intent-first specification language for describing software applications in a form that both humans and AI coding agents can use.

Start simple with one intent file, then add precision only where needed.

## Why AIM

- Keep product intent readable.
- Keep synthesis deterministic.
- Scale from lightweight specs to high-fidelity feature definitions.

## Core Idea

Each feature has one canonical intent file:

- `<feature>.intent`

Optional precision facets can be added:

- `<feature>.schema.intent`
- `<feature>.flow.intent`
- `<feature>.contract.intent`
- `<feature>.persona.intent`

This enables progressive detail:

- intent-only for speed
- partial facets for medium fidelity
- full facets for maximum precision

## Sinth — the CLI for AIM

**Synthesize intent into reality.**

AIM includes Sinth, a Python CLI tool for fetching, managing, and synthesizing packages:

```bash
pip install sinth

# Interactive menu (recommended for new users)
sinth

# Or use direct commands
sinth fetch weather

# Configure your stack
sinth config set stack.frontend "React"
sinth config set stack.backend "Node.js"

# Generate synthesis prompts
sinth synth weather
```

Sinth automatically:
- Fetches packages from the registry
- Validates intent files
- Generates formatted prompts for AI assistants
- Copies prompts to clipboard for easy pasting
- Provides guided configuration wizards

See [cli/CLI.md](./cli/CLI.md) for full documentation.

## Read The Specification

The full protocol is documented in:

- [specification.md](./specification.md)

## DigitalOcean App Platform

For custom domains and explicit `.intent` serving behavior, deploy with Docker + Nginx:

- `Dockerfile`
- `nginx.conf`
- `.do/app.yaml`

Nginx serves `*.intent` as `text/plain` and enables CORS for fetch clients.

After deploy, verify:

1. `/registry-files/index.json`
2. `/registry-files/packages/weather/weather.intent`
3. `/specification.md`

## Quick Example

```ail
AIM: game.snake#intent@1.4

INTENT SnakeGame {
  SUMMARY: "A single-player snake game with top-10 scores."
  REQUIREMENTS {
    - "Movement is tick-based."
    - "Wall and self collisions end the run."
  }

  SCHEMA GameSession {
    ATTRIBUTES {
      score: integer required min(0)
    }
  }
}
```

## Repository Layout

- [`specification.md`](./specification.md): canonical language specification
- [`registry/`](./registry): feature package registry
- [`registry/index.json`](./registry/index.json): package catalog with intent entrypoints
- [`registry/packages/`](./registry/packages): publishable feature packages (intent entry + optional facets)
- [`CONTRIBUTING.md`](./CONTRIBUTING.md): contribution and publishing workflow
- [`PROMPT.md`](./PROMPT.md): generic local AI synthesis prompt

## Current Demo

This repo includes a `game.snake` demo feature showing:

- a mixed-source intent envelope
- inline `SCHEMA`, `FLOW`, and `PERSONA`
- linked external `CONTRACT` and `VIEW` facets

It is also published as a registry package:

- [`registry/packages/game.snake`](./registry/packages/game.snake)

## Local AI Fetch Flow

Use this sequence:

1. Fetch `specification.md`.
2. Fetch `registry/index.json`.
3. Select package by `name`.
4. Fetch the package `entry` intent file and related facet files.
5. Materialize fetched sources into local `/aim` (and `/aim/mappings` when needed).
6. Synthesize from local `/aim` so users can edit and rebuild without refetching.

## Status

Current spec version: **AIM v1.4**.
