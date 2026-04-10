# ADR 005 — Palace Sync Flow: Local Mine → Azure Files → Container Restart

**Date:** 2026-04-10
**Status:** Accepted

## Context

MemPalace is a snapshot index (see ADR 007). It must be kept current manually. The palace lives locally at `.palace/`, on Azure Files at `ai-team-data/palace`, and at runtime in `/tmp/palace` inside the container.

## Decision

Palace updates follow this flow:
1. Run `mempalace mine` locally in the codespace
2. Upload updated palace to Azure Files with `az storage file upload-batch`
3. Container picks it up automatically on next restart via `start.sh`

## Rationale

- Avoids any runtime write to Azure Files (SMB incompatible)
- Local mine is fast and gives full control over what gets indexed
- No automation needed — manual flow is sufficient for now

## Commands

```bash
# Mine
MEMPALACE_PALACE_PATH=/workspaces/ai-team/.palace mempalace mine /workspaces/ai-team --wing ai_team --agent diarmuid

# Upload to Azure Files
STORAGE_KEY=$(az storage account keys list --account-name aiteamstorage001 --resource-group ai-team-rg --query "[0].value" -o tsv)
az storage file upload-batch --account-name aiteamstorage001 --account-key "$STORAGE_KEY" --destination "ai-team-data/palace" --source /workspaces/ai-team/.palace/
```

## Consequences

- Palace is always behind by at least one session unless explicitly synced
- "Wrap up" convention (see ADR 008) ensures sync happens at session end
- Future improvement: automate mine + upload on a schedule or git hook
