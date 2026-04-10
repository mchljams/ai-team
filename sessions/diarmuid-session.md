# Diarmuid — Session Notes

Dev Lead session memory. Updated at the end of each working session.

---

## Current Status

**Date:** 2026-04-10
**Phase:** ADR structure in place, palace optimised, ready for Eóin + requirements work

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
- GitHub MCP server integrated — 8 tools available (filtered from 41) for real GitHub operations
- Palace re-mined — now at 56 drawers (up from 46)
- Confirmed: conversation history is in-memory only (`defaultdict`) — lost on codespace sleep
- Planning Azure persistence stack (see Key Decisions and Open Items)
- **v7 deployed**: Fixed 413 token overflow — session notes truncated to last 4000 chars, history limit 20→8, palace recall reduced
- **Diarmuid VS Code agent created**: `.github/agents/Diarmuid.agent.md` — select from agent picker to use Diarmuid as primary interface in VS Code
- Palace reset and re-mined to 105 drawers — ADRs in `documentation` room, properly indexed
- `docs/requirements/` placeholder created — ready for Eóin's output
- `mempalace.yaml` auto-configured with `documentation` and `planning` rooms
- `entities.json` updated, `.devcontainer/devcontainer.json` committed
- Azure Files palace synced — Slack Diarmuid picks up all ADR content on next restart
- Everything committed and pushed — `feat/mcp-github-tools` branch clean
- **COMPLETED: Azure Container Apps deployment** — Diarmuid is now always-on in Azure
  - Resource group: `ai-team-rg` (eastus)
  - Storage account: `aiteamstorage001`, Azure Files share: `ai-team-data` (mounted at `/data`)
  - Container Registry: `aiteamregistry.azurecr.io`
  - Container App: `diarmuid`, current image `diarmuid-listener:v6`, min-replicas=1
  - Palace: uploaded to Azure Files `ai-team-data/palace` (3.1MB, 83 drawers); copied to `/tmp/palace` at startup via `start.sh`
  - SQLite conversation DB: `/tmp/conversations.db` (instance-local; palace captures long-term memory)
  - Secrets stored in Container Apps: `DIARMUID_SLACK_TOKEN`, `DIARMUID_SLACK_APP_TOKEN`, `AI_TEAM_PAT`/`GITHUB_MODELS_TOKEN`
  - Confirmed responding in Slack ✅
- **v5/v6 fixes deployed**:
  - v5: Pre-warmed ChromaDB embedding model (`all-MiniLM-L6-v2`, 79MB) in Dockerfile — was downloading per message
  - v6: `scripts/start.sh` entrypoint copies palace from Azure Files `/data/palace` → `/tmp/palace` at startup before listener starts
  - SMB incompatibility confirmed for both SQLite and ChromaDB — all runtime file I/O must use `/tmp`
  - Palace (83 drawers, 3.1MB) uploaded to Azure Files share at `ai-team-data/palace`
  - v6 startup confirmed: palace copied, `⚡️ Bolt app is running!`

## Key Decisions

Decisions are recorded individually in `docs/decisions/`. Current ADRs:

- [001](../docs/decisions/001-azure-over-flyio.md) — Azure Container Apps over Fly.io
- [002](../docs/decisions/002-smb-incompatibility-tmp-pattern.md) — SMB incompatibility: all runtime I/O must use /tmp
- [003](../docs/decisions/003-conversation-history-sqlite-tmp.md) — Conversation history: SQLite in /tmp
- [004](../docs/decisions/004-start-sh-palace-copy-pattern.md) — start.sh: copy palace from Azure Files to /tmp at startup
- [005](../docs/decisions/005-palace-sync-flow.md) — Palace sync flow: local mine → Azure Files → container restart
- [006](../docs/decisions/006-chromadb-model-prewarm.md) — ChromaDB model must be pre-warmed in Docker image
- [007](../docs/decisions/007-vscode-primary-interface.md) — VS Code (Diarmuid agent) is the primary interface
- [008](../docs/decisions/008-mempalace-snapshot-not-live.md) — MemPalace is a snapshot index, not a live journal
- [009](../docs/decisions/009-session-end-wrap-up-convention.md) — Session end convention: "wrap up"
- [010](../docs/decisions/010-llm-backend-gpt4o-to-claude.md) — LLM: GPT-4o now, Claude Sonnet when Anthropic credits added
- [011](../docs/decisions/011-acr-versioned-image-tags.md) — ACR: always use versioned image tags
- [012](../docs/decisions/012-acr-managed-identity-acrpull.md) — ACR pull auth via managed identity + AcrPull role

## Open Items

- **Next session priority**: Create Eóin VS Code agent + start writing requirements with Eóin
- **Add `scripts/restore-palace.sh`**: Downloads palace from Azure Files to local `.palace/` — needed on codespace rebuild. Run: `az storage file download-batch --source ai-team-data/palace --destination /workspaces/ai-team/.palace/`
- Add Anthropic API credits → generate key → add as `ANTHROPIC_API_KEY` → switch Slack listener to Claude Sonnet (removes 8k token limit permanently)
- Apply updated manifests for Eóin's bot when ready
- Set up Eóin Slack listener when needed
- Consider automated `mempalace mine` on a schedule inside the container
- After each significant session: re-mine palace locally and upload to Azure Files (keeps Diarmuid's long-term memory current)

## Notes

- **Codespace listener no longer needed** — Diarmuid runs from Azure Container Apps permanently
- Azure Container App: `diarmuid` in `ai-team-rg`, eastus, image `aiteamregistry.azurecr.io/diarmuid-listener:v6`
- To update Diarmuid: build new image, push to ACR with new version tag, `az containerapp update --name diarmuid --resource-group ai-team-rg --image aiteamregistry.azurecr.io/diarmuid-listener:vN`
- To check logs: `az containerapp logs show --name diarmuid --resource-group ai-team-rg --tail 50`
- To sync palace to Azure after re-mining:
  ```bash
  STORAGE_KEY=$(az storage account keys list --account-name aiteamstorage001 --resource-group ai-team-rg --query "[0].value" -o tsv)
  az storage file upload-batch --account-name aiteamstorage001 --account-key "$STORAGE_KEY" --destination "ai-team-data/palace" --source /workspaces/ai-team/.palace/
  ```
- Eóin does not have repo access — session memory is Diarmuid-only for now
- Socket Mode requires an App-Level Token (`xapp-...`) with `connections:write` scope — named `diarmuid-socket` in Slack
- Listener responds to DMs automatically; in channels responds to @mentions only
- Claude API requires paid credits (separate from Claude.ai subscription) — deferred, using GPT-4o free tier
- Anthropic models not available on GitHub Models endpoint
