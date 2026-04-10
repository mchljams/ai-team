# ADR 003 — Conversation History: SQLite in /tmp (Not Azure Files)

**Date:** 2026-04-10
**Status:** Accepted

## Context

Original implementation used an in-memory `defaultdict` for conversation history — lost whenever the codespace slept or the process restarted. Needed a persistent replacement.

## Decision

Use SQLite at `/tmp/conversations.db` for conversation history. Do not attempt to persist it to Azure Files.

## Rationale

- SQLite is a stdlib dependency — no extra packages
- `/tmp` avoids the SMB locking issue (see ADR 002)
- Conversation history is session-scoped; losing it on restart is acceptable
- Long-term memory is the responsibility of MemPalace (see ADR 007), not conversation history

## Consequences

- History survives Slack disconnects and reconnects within the same container lifecycle
- History is lost on container restart — by design
- Schema: `conversations(id, user_id, role, content, created_at)` with index on `user_id`
- History limited to last 8 messages per user to stay within GPT-4o 8k token limit
