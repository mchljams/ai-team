#!/bin/bash
# Startup script: copy palace from Azure Files to /tmp for fast local access
# ChromaDB does not work reliably on SMB (Azure Files) — use /tmp at runtime.

AZURE_PALACE=/data/palace
LOCAL_PALACE=/tmp/palace

if [ -d "$AZURE_PALACE" ]; then
    echo "Copying palace from Azure Files to /tmp/palace..."
    cp -r "$AZURE_PALACE" "$LOCAL_PALACE"
    echo "Palace copied ($(du -sh $LOCAL_PALACE | cut -f1))"
else
    echo "No palace found at $AZURE_PALACE — starting without memory"
fi

export MEMPALACE_PALACE_PATH="$LOCAL_PALACE"

exec python3 /app/scripts/diarmuid-listener.py
