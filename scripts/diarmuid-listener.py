#!/usr/bin/env python3
"""
Diarmuid (Dev Lead) — Slack Socket Mode listener with GitHub Models LLM backend
and MemPalace memory integration.

Requires environment variables:
  DIARMUID_SLACK_TOKEN      Bot token (xoxb-...)
  DIARMUID_SLACK_APP_TOKEN  App-level token (xapp-...)
  GITHUB_MODELS_TOKEN       GitHub PAT with models:read scope

Install dependencies:
  pip install slack-bolt openai mempalace

Run:
  python3 scripts/diarmuid-listener.py
"""

import os
import pathlib
from collections import defaultdict
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Import MemPalace memory stack
try:
    from mempalace.layers import MemoryStack
    from mempalace.searcher import search_memories
    import chromadb
    from datetime import datetime, timezone
    import uuid as _uuid
    PALACE_PATH = str(pathlib.Path(__file__).parent.parent / ".palace")
    memory_stack = MemoryStack(palace_path=PALACE_PATH)
    MEMORY_ENABLED = True
    print(f"MemPalace loaded from {PALACE_PATH}")
except Exception as e:
    MEMORY_ENABLED = False
    print(f"MemPalace not available: {e}")

SLACK_TOKEN = os.environ.get("DIARMUID_SLACK_TOKEN")
SLACK_APP_TOKEN = os.environ.get("DIARMUID_SLACK_APP_TOKEN")
GITHUB_MODELS_TOKEN = os.environ.get("GITHUB_MODELS_TOKEN")

if not SLACK_TOKEN:
    raise SystemExit("ERROR: DIARMUID_SLACK_TOKEN is not set")
if not SLACK_APP_TOKEN:
    raise SystemExit("ERROR: DIARMUID_SLACK_APP_TOKEN is not set")
if not GITHUB_MODELS_TOKEN:
    raise SystemExit("ERROR: GITHUB_MODELS_TOKEN is not set")

# Load context files
ROOT = pathlib.Path(__file__).parent.parent
PERSONA = (ROOT / "personas" / "DevLead.md").read_text()
TEAM = (ROOT / "TEAM.md").read_text()
SESSION = (ROOT / "sessions" / "diarmuid-session.md").read_text()

SYSTEM_PROMPT = f"""{PERSONA}

---

## Team State

{TEAM}

---

## Session Notes

{SESSION}
"""

# GitHub Models uses the OpenAI-compatible endpoint
llm = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=GITHUB_MODELS_TOKEN,
)

MODEL = "gpt-4o"

# Per-user conversation history (in-memory, resets on restart)
conversation_history = defaultdict(list)

app = App(token=SLACK_TOKEN)


def recall_from_palace(query: str) -> str:
    """Search MemPalace for relevant context to augment the response."""
    if not MEMORY_ENABLED:
        return ""
    try:
        results = search_memories(
            query=query,
            palace_path=PALACE_PATH,
            n_results=3,
        )
        if not results:
            return ""
        snippets = []
        for r in results:
            snippets.append(f"[{r.get('wing','')}/{r.get('room','')}] {r.get('document','')[:300]}")
        return "\n\n---\nRelevant memory:\n" + "\n\n".join(snippets)
    except Exception:
        return ""


def file_to_palace(user: str, human_text: str, ai_reply: str) -> None:
    """Write a conversation exchange to the palace as a drawer."""
    if not MEMORY_ENABLED:
        return
    try:
        client = chromadb.PersistentClient(path=PALACE_PATH)
        col = client.get_or_create_collection("mempalace_drawers")
        now = datetime.now(timezone.utc).isoformat()
        content = f"[Slack DM — {now}]\nUser: {human_text}\nDiarmuid: {ai_reply}"
        col.add(
            ids=[str(_uuid.uuid4())],
            documents=[content],
            metadatas=[{
                "wing": "ai_team",
                "room": "sessions",
                "source_file": "slack-dm",
                "agent": "diarmuid",
                "filed_at": now,
            }],
        )
    except Exception as e:
        print(f"Palace write failed: {e}")


def ask_diarmuid(user_id: str, text: str) -> str:
    history = conversation_history[user_id]

    # Augment prompt with palace recall
    memory_context = recall_from_palace(text)
    augmented_text = text
    if memory_context:
        augmented_text = f"{text}\n{memory_context}"

    history.append({"role": "user", "content": augmented_text})

    # Keep history to last 20 messages to avoid token overflow
    trimmed = history[-20:]

    response = llm.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + trimmed,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    # Write exchange to palace for persistent memory
    file_to_palace(user_id, text, reply)
    return reply


@app.event("app_mention")
def handle_mention(event, say):
    if event.get("bot_id"):
        return
    user = event.get("user", "unknown")
    text = event.get("text", "")
    reply = ask_diarmuid(user, text)
    say(reply)


@app.event("message")
def handle_message(event, say):
    # Ignore bot messages to prevent loops
    if event.get("bot_id"):
        return
    channel_type = event.get("channel_type", "")
    # In channels only respond to mentions (handled above); respond to all DMs
    if channel_type != "im":
        return
    user = event.get("user", "unknown")
    text = event.get("text", "")
    reply = ask_diarmuid(user, text)
    say(reply)


if __name__ == "__main__":
    print("Diarmuid listener starting (Socket Mode + GitHub Models + MemPalace)...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
