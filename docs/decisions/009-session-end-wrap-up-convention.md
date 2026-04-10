# ADR 009 — Session End Convention: "Wrap Up"

**Date:** 2026-04-10
**Status:** Accepted

## Context

VS Code has no session end event. Without a convention, session notes go stale, the palace falls behind, and the next session starts without full context.

## Decision

When Mike says **"wrap up"**, Diarmuid performs the full end-of-session routine without being asked for each step.

## Routine

1. Update `sessions/diarmuid-session.md` — current status, any new completed items, key decisions, open items
2. Extract any significant new decisions to `docs/decisions/` as individual ADR files
3. Run `mempalace mine` locally
4. Upload palace to Azure Files
5. `git add`, `git commit`, `git push` all changes

## Rationale

- Simple, memorable trigger word
- Ensures each new session starts clean — Diarmuid reads fresh notes and is immediately oriented
- Palace is kept within one session of current

## Consequences

- No automation required — human trigger is reliable enough for now
- If Mike leaves without saying "wrap up", next session may start with stale context
- Future option: VS Code hook or git pre-push hook to automate parts of this
