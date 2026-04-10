# ADR 011 — Azure Container Registry: Always Use Versioned Image Tags

**Date:** 2026-04-10
**Status:** Accepted

## Context

During initial deployment, images were tagged `:latest`. Azure Container Apps cached the `latest` digest and would not pull a new image even after `docker push`, causing deployments to silently run the old code.

## Decision

Always tag images with an explicit version (`:v1`, `:v2`, etc.) in addition to or instead of `:latest`. Always update the Container App to the new versioned tag.

## Commands

```bash
docker build -t aiteamregistry.azurecr.io/diarmuid-listener:vN .
docker push aiteamregistry.azurecr.io/diarmuid-listener:vN
az containerapp update --name diarmuid --resource-group ai-team-rg \
  --image aiteamregistry.azurecr.io/diarmuid-listener:vN
```

## Consequences

- Current live image: `diarmuid-listener:v7`
- Each deployment increments the version tag
- Old images remain in ACR — clean up periodically if storage becomes a concern
