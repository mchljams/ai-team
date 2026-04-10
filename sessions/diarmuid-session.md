# Diarmuid — Session Notes

Dev Lead session memory. Updated at the end of each working session.

---

## Current Status

**Date:** 2026-04-10
**Phase:** VS Code Diarmuid agent created — primary interface established

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
- Palace re-mined to 87 drawers and synced to Azure Files
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

## Key Decisions Made This Session

- **Slack manifest editor**: Slack's YAML editor has quirks — use JSON tab or configure via sidebar directly
- **Socket Mode**: Configured via Settings → Socket Mode in Slack dashboard before manifest will accept it
- **Event subscriptions**: `app_mention`, `message.channels`, `message.im` added via sidebar, then reinstall
- **MemPalace over flat session notes**: Palace is the deep searchable layer; session notes are the fast always-fresh layer — both kept for now
- **GPT-4o over Claude**: Anthropic API requires paid credits (separate from Claude.ai subscription). Deferred — using GitHub Models free tier. Next step to become "the same Diarmuid" is to add Anthropic API credits and switch the listener to Claude 3.5 Sonnet
- **Persistent Diarmuid roadmap**: Stage 1 (done) = palace + session notes; Stage 2 = SQLite conversation history; Stage 3 = Fly.io always-on; Stage 4 = unified backend
- **Azure over Fly.io**: Switched target deployment from Fly.io to Azure Container Apps — better fit for persistent volume (Azure Files) to keep palace and conversation history alive across restarts/sleeps
- **Azure persistence stack**:
  - Azure Container Apps — always-on listener
  - Azure Files share — mounted volume for `.palace/` (ChromaDB) and `conversations.db` (SQLite)
  - Container Apps built-in secrets — for Slack tokens, GitHub PAT
  - Conversation history: SQLite on shared volume (replaces in-memory `defaultdict`)
- **Lost context problem**: Codespace sleep kills both the listener process and in-memory conversation history. Azure deployment solves this permanently.

- **VS Code is the primary interface for doing work**: Slack is for async/away status checks only. VS Code Diarmuid agent has full tool access, no token limits, and reads session notes at start of each session for full context continuity.
- **MemPalace is a snapshot index, not a live journal**: `mempalace mine` reads files and builds a searchable vector index. It does not passively record conversations. It only knows what was in files at the time of last `mine` run. Sessions notes + periodic mine is the right pattern.
- **Session end convention**: Say "wrap up" — Diarmuid updates session notes, re-mines palace, uploads to Azure Files, commits. This is what makes the next session start clean.
- **SMB incompatibility is broader than SQLite**: ChromaDB also fails on Azure Files SMB (lock patterns during search). All runtime file I/O (SQLite + ChromaDB) must use `/tmp`. Palace is treated as read-only at runtime — copied from Azure Files to `/tmp` at startup, never written back.
- **`start.sh` pattern**: Entrypoint script copies palace from `/data/palace` (Azure Files) → `/tmp/palace`, sets `MEMPALACE_PALACE_PATH=/tmp/palace`, then execs the listener. Solves SMB locking for ChromaDB permanently.
- **ChromaDB embedding model pre-warm**: `all-MiniLM-L6-v2` (79MB) must be baked into Docker image — add `RUN python3 -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()([\"\"])"` to Dockerfile. Without this it downloads on every container restart.
- **Palace sync flow**: Local `mempalace mine` → upload to Azure Files with `az storage file upload-batch` → next container restart picks it up automatically via `start.sh` copy.
- **SQLite on Azure Files — incompatible**: SMB file locking breaks SQLite. Solution: SQLite in `/tmp` (instance-local for session history), palace on Azure Files (persistent long-term memory). This is the right split.
- **Azure image tagging**: Always use versioned tags (`:v1`, `:v2` etc.) not just `:latest` — Container Apps caches `latest` and won't pull a new image without a tag change.
- **ACR + managed identity**: Container App system identity needs `AcrPull` role assigned on the registry before deployment will succeed.
- **Resource provider registration**: Fresh Azure free trial needs all providers registered manually (`Microsoft.Storage`, `Microsoft.ContainerRegistry`, `Microsoft.App`, `Microsoft.OperationalInsights`) — takes ~2 min each.

## Open Items

- **Next session priority**: Create Eóin VS Code agent + start writing requirements with Eóin
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
