# ADR 001 — Azure Container Apps over Fly.io

**Date:** 2026-04-10
**Status:** Accepted

## Context

Diarmuid needed a persistent, always-on deployment to solve the "codespace sleep kills the listener" problem. Fly.io was the initial candidate. Azure was also available due to a free trial being started.

## Decision

Deploy Diarmuid's Slack listener to Azure Container Apps, not Fly.io.

## Rationale

- Azure Files provides a native persistent volume (SMB share) — no extra config for durable storage
- Azure Container Registry integrates natively with Container Apps for image pulls
- Managed identity handles ACR auth without storing credentials
- Azure free trial was already active — no new account needed
- Container Apps supports min-replicas=1 (always-on) out of the box

## Consequences

- All Azure resources in `ai-team-rg` (eastus): ACR `aiteamregistry.azurecr.io`, Container App `diarmuid`, storage `aiteamstorage001`, Files share `ai-team-data`
- Subscription: `083a5692-ca7a-40b7-bf03-da9aa017a432`
- Cost: covered under free trial; review when trial expires
