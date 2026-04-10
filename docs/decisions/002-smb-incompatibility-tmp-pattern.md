# ADR 002 — SMB Incompatibility: All Runtime File I/O Must Use /tmp

**Date:** 2026-04-10
**Status:** Accepted

## Context

Azure Files is mounted via SMB into the Container App at `/data`. Both SQLite and ChromaDB were initially pointed at paths under `/data`. Both failed with file locking errors:
- SQLite: `database is locked`
- ChromaDB: lock pattern failures during search queries, causing every Slack message to hang indefinitely

## Decision

All runtime file I/O (SQLite, ChromaDB) must use `/tmp`. Azure Files (`/data`) is treated as a **read-only source** at container startup only.

## Rationale

SMB does not support the POSIX file locking primitives that both SQLite and ChromaDB require. This is a fundamental protocol limitation, not a configuration issue.

## Consequences

- SQLite conversation DB: `/tmp/conversations.db` — instance-local, lost on restart (acceptable; long-term memory is the palace)
- ChromaDB palace: copied from `/data/palace` → `/tmp/palace` at startup via `start.sh`
- Writes to `/tmp` during runtime do NOT persist back to Azure Files automatically
- See ADR 004 for the start.sh pattern
- See ADR 005 for the palace sync flow
