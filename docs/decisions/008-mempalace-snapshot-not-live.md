# ADR 008 — MemPalace Is a Snapshot Index, Not a Live Journal

**Date:** 2026-04-10
**Status:** Accepted

## Context

Initial assumption was that MemPalace would passively record conversations and stay continuously up to date — a "live journal". This was incorrect.

## Decision

Treat MemPalace as a **searchable snapshot index** over project files, not continuous memory.

## How It Actually Works

- `mempalace mine` reads specified files, chunks them into "drawers", stores in ChromaDB with vector embeddings
- Semantic search (`mempalace search`) retrieves relevant chunks by query
- No passive recording — it only knows what was in files at the time of the last `mine` run
- Two layers of memory: palace (searchable, deep) + session notes (always-fresh, linear)

## Rationale

This is the correct model for the tool. Trying to make it a live journal would require either:
- A persistent database both instances query (Postgres etc.), or
- Writing markdown log files to Azure Files after conversations, then mining them

Neither is worth the complexity at this stage. Session notes serve the "fast fresh layer" role well.

## Consequences

- Palace value scales with content diversity — one big session notes file mines poorly; many small specific files mine well
- Key decisions should live in individual ADR files (see `docs/decisions/`)
- Requirements will live in `docs/requirements/` — Eóin's output feeds the palace
- Mine + sync at "wrap up" is sufficient for now
