# Diarmuid — Session Notes

Dev Lead session memory. Updated at the end of each working session.

---

## Current Status

**Date:** 2026-04-10
**Phase:** Slack listener live with LLM + MemPalace memory

---

## Completed

- Inaugural task completed (prior session)
- Dev Lead persona defined: `personas/DevLead.md`
- Session prompt created: `personas/DevLead.prompt.md`
- Slack bot configured: `slack/diarmuid-devlead-slack-manifest.json`
- Slack tokens added to GitHub Codespaces secrets (`DIARMUID_SLACK_TOKEN`, `EOIN_SLACK_TOKEN`)
- Slack connectivity test script created: `scripts/test-slack-bots.sh`
- Both bots tested and confirmed live — posting to Slack successfully
- Socket Mode enabled on Diarmuid Slack app — App-Level Token created (`diarmuid-socket`)
- `DIARMUID_SLACK_APP_TOKEN` added to Codespaces secrets
- Socket Mode listener created: `scripts/diarmuid-listener.py`
- Listener connected to GPT-4o via GitHub Models API (`AI_TEAM_PAT` with `models:read` scope)
- MemPalace installed and initialised — palace at `.palace/`
- 46 drawers mined from project files (personas, TEAM.md, sessions, manifests, scripts)
- Listener augments every response with semantic palace recall — memory is live

## Key Decisions Made This Session

- **Slack manifest editor**: Slack's YAML editor has quirks — use JSON tab or configure via sidebar directly
- **Socket Mode**: Configured via Settings → Socket Mode in Slack dashboard before manifest will accept it
- **Event subscriptions**: `app_mention`, `message.channels`, `message.im` added via sidebar, then reinstall
- **MemPalace over flat session notes**: Palace is the deep searchable layer; session notes are the fast always-fresh layer — both kept for now
- **GPT-4o over Claude**: Anthropic API requires paid credits (separate from Claude.ai subscription). Deferred — using GitHub Models free tier. Next step to become "the same Diarmuid" is to add Anthropic API credits and switch the listener to Claude 3.5 Sonnet
- **Persistent Diarmuid roadmap**: Stage 1 (done) = palace + session notes; Stage 2 = SQLite conversation history; Stage 3 = Fly.io always-on; Stage 4 = unified backend

## Open Items

- Add Anthropic API credits → generate key → add as `ANTHROPIC_API_KEY` → switch listener to Claude Sonnet (this makes Slack "the same Diarmuid")
- Apply updated manifests for Eóin's bot when ready
- Set up Eóin listener when needed
- Consider Fly.io deployment for always-on listener (deferred)
- Re-mine palace after significant updates (`MEMPALACE_PALACE_PATH=/workspaces/ai-team/.palace mempalace mine /workspaces/ai-team --wing ai_team --agent diarmuid`)

## Notes

- Listener start command: `export GITHUB_MODELS_TOKEN=$AI_TEAM_PAT && MEMPALACE_PALACE_PATH=/workspaces/ai-team/.palace python3 scripts/diarmuid-listener.py`
- Eóin does not have repo access — session memory is Diarmuid-only for now
- The `#general` channel must exist in Slack before `test-slack-bots.sh` will succeed
- Socket Mode requires an App-Level Token (`xapp-...`) with `connections:write` scope — named `diarmuid-socket` in Slack
- Listener responds to DMs automatically; in channels responds to @mentions only
- Claude API requires paid credits (separate from Claude.ai subscription) — deferred, using GPT-4o free tier
- Anthropic models not available on GitHub Models endpoint
- The Slack bot is GPT-4o reasoning through the Diarmuid persona — same character, different engine. Switching to Claude Sonnet on Anthropic API would make it genuinely the same model as VS Code Copilot
