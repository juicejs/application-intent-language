# Application Intent Language (AIL)

AIL is an intent-first specification language for describing software features in a form that both humans and AI coding agents can use.

Start simple with one intent file, then add precision only where needed.

## Why AIL

- Keep product intent readable.
- Keep synthesis deterministic.
- Scale from lightweight specs to high-fidelity feature definitions.

## Core Idea

Each feature has one canonical intent file:

- `<feature>.intent.ail`

Optional precision facets can be added:

- `<feature>.schema.ail`
- `<feature>.flow.ail`
- `<feature>.contract.ail`
- `<feature>.persona.ail`

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
AIL: game.snake#intent@1.4

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
- [`ail/`](./ail): example feature sources
- [`ail/game.snake.intent.ail`](./ail/game.snake.intent.ail): intent envelope example
- [`registry/`](./registry): feature package registry
- [`registry/packages/`](./registry/packages): publishable feature packages
- [`CONTRIBUTING.md`](./CONTRIBUTING.md): contribution and publishing workflow
- [`test/`](./test): test workspace and tooling

## Current Demo

This repo includes a `game.snake` demo feature showing:

- intent envelope with `INCLUDES`
- linked external facets (`schema`, `flow`, `contract`, `persona`)

It is also published as a registry package:

- [`registry/packages/game.snake`](./registry/packages/game.snake)

## Status

Current spec version: **AIL v1.4**.
