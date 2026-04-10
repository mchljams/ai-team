# ADR 007 — VS Code (Diarmuid Agent) Is the Primary Interface for Work

**Date:** 2026-04-10
**Status:** Accepted

## Context

Two interfaces exist for interacting with Diarmuid: VS Code (this agent) and Slack (Azure Container App). Initially unclear which should be the primary working surface.

## Decision

VS Code with the Diarmuid agent (`.github/agents/Diarmuid.agent.md`) is the primary interface for all substantive work. Slack is for async, away-from-desk status checks only.

## Rationale

| Capability | VS Code | Slack |
|---|---|---|
| File read/write | ✅ | ❌ |
| Run commands / deploy | ✅ | ❌ |
| Context window | ~200k (Claude) | 8k (GPT-4o) |
| Palace access | ✅ full | ❌ snapshot only |

Slack Diarmuid is architecturally limited by GPT-4o's 8k token limit. The system prompt alone consumes ~3,900 tokens, leaving little room for history or complex reasoning.

## Consequences

- The Diarmuid VS Code agent reads `sessions/diarmuid-session.md` at session start for full context
- Slack remains useful for: "is it deployed?", "what's the status?", quick async direction
- Long-term: switching Slack listener to Claude Sonnet (Anthropic credits needed) will close most of this gap
- Agent file: `.github/agents/Diarmuid.agent.md`
