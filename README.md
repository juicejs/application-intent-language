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

## Read The Specification

The full protocol is documented in:

- [specification.md](./specification.md)

## GitHub Pages

This repository ships a static site from `/site` with:

- `/` overview
- `/spec/` specification entry
- `/registry/` package registry entry

Deployment is automated by:

- `.github/workflows/pages.yml`

To enable it in GitHub:

1. Open repository `Settings -> Pages`.
2. Set `Source` to `GitHub Actions`.
3. Push to `main` or run the workflow manually.

## Quick Example

```ail
AIM: game.snake#intent@1.4

INTENT SnakeGame {
  SUMMARY: "A single-player snake game with top-10 scores."
  REQUIREMENTS:
    - Movement is tick-based.
    - Wall and self collisions end the run.

  SCHEMA: |
    entities:
      - name: GameSession
        fields:
          - name: score
            type: integer
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

- intent envelope with `INCLUDES`
- linked external facets (`schema`, `flow`, `contract`, `persona`)

It is also published as a registry package:

- [`registry/packages/game.snake`](./registry/packages/game.snake)

## Local AI Fetch Flow

Use this sequence:

1. Fetch `specification.md`.
2. Fetch `registry/index.json`.
3. Select package by `name`.
4. Fetch the package `entry` intent file and related facet files.
5. Materialize fetched sources into local `/ail` (and `/ail/mappings` when needed).
6. Synthesize from local `/ail` so users can edit and rebuild without refetching.

## Status

Current spec version: **AIM v1.4**.
