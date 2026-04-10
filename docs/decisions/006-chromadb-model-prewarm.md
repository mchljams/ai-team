# ADR 006 — ChromaDB Embedding Model Must Be Pre-Warmed in Docker Image

**Date:** 2026-04-10
**Status:** Accepted

## Context

On first use, ChromaDB downloads the `all-MiniLM-L6-v2` sentence embedding model (~79MB) from HuggingFace. In the container this was happening on every message that triggered a palace search, adding several seconds of latency and risk of download failures.

## Decision

Pre-warm the embedding model at Docker image build time.

## Rationale

- 79MB download at runtime is slow, unreliable, and wasteful
- Baking it into the image adds ~80MB to image size but eliminates the runtime cost
- Model is stable — doesn't need to be refreshed frequently

## Implementation

Add to Dockerfile during build:
```dockerfile
RUN python3 -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()([\"\"])"
```

## Consequences

- Docker image is ~80MB larger
- No model download at runtime — palace search responds immediately
- If the model needs updating, rebuild the image
- First introduced in `diarmuid-listener:v5`
