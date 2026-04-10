# ADR 004 — start.sh: Copy Palace from Azure Files to /tmp at Startup

**Date:** 2026-04-10
**Status:** Accepted

## Context

ChromaDB palace needs to be available at runtime but cannot be used directly from Azure Files (see ADR 002). The palace must be on a local path for ChromaDB to read without locking errors.

## Decision

Use `scripts/start.sh` as the container entrypoint. It copies the palace from `/data/palace` (Azure Files mount) to `/tmp/palace` before starting the listener.

## Rationale

- Simple and reliable — no code changes to the listener required
- Palace is treated as read-only at runtime, which is correct (it's a mined snapshot)
- Sets `MEMPALACE_PALACE_PATH=/tmp/palace` env var before exec-ing the listener
- Startup cost is minimal (~1-2 seconds for 3-4MB palace)

## Consequences

- `start.sh` must remain the `CMD` in the Dockerfile
- Palace writes during runtime (e.g. `_file_to_palace_sync`) go to `/tmp/palace` — lost on restart
- Palace updates require: local `mempalace mine` → `az storage file upload-batch` → container restart
- See ADR 005 for the full sync flow
