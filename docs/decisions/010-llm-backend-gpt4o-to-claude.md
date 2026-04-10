# ADR 010 — LLM Backend: GPT-4o Now, Claude Sonnet When Anthropic Credits Available

**Date:** 2026-04-10
**Status:** Partially superseded (VS Code uses Claude; Slack still uses GPT-4o)

## Context

Two LLM options were considered for Diarmuid's backend: GitHub Models (GPT-4o, free tier) and Anthropic Claude Sonnet. Claude was the preference due to larger context window (200k vs 8k).

## Decision

Use GitHub Models GPT-4o for the Slack listener now. Switch to Claude Sonnet when Anthropic API credits are added.

VS Code Diarmuid agent uses Claude Sonnet directly (no API key needed — VS Code Copilot provides it).

## Rationale

- Anthropic API requires paid credits separate from Claude.ai subscription
- GitHub Models free tier is sufficient for bootstrapping
- GPT-4o 8k limit is a real constraint for Slack Diarmuid — workarounds in place (session truncation, reduced history)
- VS Code agent already has Claude — the full context window is available for work sessions

## Consequences

- Slack Diarmuid is limited to 8k tokens — verbose responses cause 413 errors
- Mitigation: session notes truncated to 4000 chars, history limit 8 msgs, palace recall 2×200 chars
- **Open item**: Add Anthropic credits → `ANTHROPIC_API_KEY` secret → update listener model
- Token: `AI_TEAM_PAT` (GitHub PAT with `models:read`) used for GitHub Models endpoint
