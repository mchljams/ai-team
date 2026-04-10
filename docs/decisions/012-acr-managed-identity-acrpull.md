# ADR 012 — ACR Pull Auth: Managed Identity with AcrPull Role

**Date:** 2026-04-10
**Status:** Accepted

## Context

Container App deployments initially failed because the app could not pull the image from ACR. The Container App was using its system-assigned managed identity but it had not been granted any permissions on the registry.

## Decision

Assign the `AcrPull` role to the Container App's system-assigned managed identity on the ACR scope.

## Implementation

```bash
# Get the managed identity principal ID
PRINCIPAL=$(az containerapp show --name diarmuid --resource-group ai-team-rg \
  --query "identity.principalId" -o tsv)

# Get the ACR resource ID
ACR_ID=$(az acr show --name aiteamregistry --resource-group ai-team-rg --query id -o tsv)

# Assign AcrPull
az role assignment create --assignee "$PRINCIPAL" --role AcrPull --scope "$ACR_ID"
```

## Consequences

- Managed identity principal: `2bb57375-e9b2-496b-a338-a8ce217129e5`
- No stored credentials — auth is handled by Azure RBAC
- Any new Container App pulling from this ACR needs the same role assignment
