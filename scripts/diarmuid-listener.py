#!/usr/bin/env python3
"""
Diarmuid (Dev Lead) — Slack Socket Mode listener with GitHub Models LLM backend,
MemPalace memory integration, and GitHub MCP Server tool execution.

Requires environment variables:
  DIARMUID_SLACK_TOKEN      Bot token (xoxb-...)
  DIARMUID_SLACK_APP_TOKEN  App-level token (xapp-...)
  GITHUB_MODELS_TOKEN       GitHub PAT with models:read scope
  AI_TEAM_PAT               GitHub PAT used by MCP server (create branches, PRs, etc.)

Install dependencies:
  pip install slack-bolt aiohttp openai mempalace mcp

Run:
  export GITHUB_MODELS_TOKEN=$AI_TEAM_PAT
  MEMPALACE_PALACE_PATH=/workspaces/ai-team/.palace python3 scripts/diarmuid-listener.py
"""

import asyncio
import json
import os
import pathlib
from collections import defaultdict
from typing import Optional

from openai import AsyncOpenAI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# MemPalace — optional, degrades gracefully if unavailable
try:
    from mempalace.searcher import search_memories
    import chromadb
    from datetime import datetime, timezone
    import uuid as _uuid
    PALACE_PATH = os.environ.get(
        "MEMPALACE_PALACE_PATH",
        str(pathlib.Path(__file__).parent.parent / ".palace"),
    )
    MEMORY_ENABLED = True
    print(f"MemPalace loaded from {PALACE_PATH}")
except Exception as e:
    MEMORY_ENABLED = False
    print(f"MemPalace not available: {e}")

# ── Environment ────────────────────────────────────────────────────────────────
SLACK_TOKEN = os.environ.get("DIARMUID_SLACK_TOKEN")
SLACK_APP_TOKEN = os.environ.get("DIARMUID_SLACK_APP_TOKEN")
GITHUB_MODELS_TOKEN = os.environ.get("GITHUB_MODELS_TOKEN")
GITHUB_PAT = os.environ.get("AI_TEAM_PAT") or GITHUB_MODELS_TOKEN
MCP_BINARY = str(pathlib.Path(__file__).parent.parent / "bin" / "github-mcp-server")

if not SLACK_TOKEN:
    raise SystemExit("ERROR: DIARMUID_SLACK_TOKEN is not set")
if not SLACK_APP_TOKEN:
    raise SystemExit("ERROR: DIARMUID_SLACK_APP_TOKEN is not set")
if not GITHUB_MODELS_TOKEN:
    raise SystemExit("ERROR: GITHUB_MODELS_TOKEN is not set")

# ── Context files ──────────────────────────────────────────────────────────────
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

---

## Important Constraints

You are running as a Slack bot with access to GitHub tools via MCP. You CAN execute GitHub
operations (create branches, open PRs, read files, push commits, etc.) using the available tools.
However, you CANNOT run arbitrary shell commands or access the local filesystem beyond what the
tools provide. Always use tools when action is needed rather than describing what you would do.
If a tool fails, report the actual error honestly. Never narrate performing an action you are not
actually performing.
"""

# ── LLM client ─────────────────────────────────────────────────────────────────
llm = AsyncOpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=GITHUB_MODELS_TOKEN,
)
MODEL = "gpt-4o"

# ── Global MCP state (populated at startup) ────────────────────────────────────
openai_tools: list = []
mcp_session: Optional[ClientSession] = None

# ── Per-user conversation history (in-memory) ─────────────────────────────────
conversation_history: dict = defaultdict(list)

app = AsyncApp(token=SLACK_TOKEN)


# ── Memory helpers ─────────────────────────────────────────────────────────────

def _recall_sync(query: str) -> str:
    if not MEMORY_ENABLED:
        return ""
    try:
        results = search_memories(query=query, palace_path=PALACE_PATH, n_results=3)
        if not results:
            return ""
        snippets = [
            f"[{r.get('wing','')}/{r.get('room','')}] {r.get('document','')[:300]}"
            for r in results
        ]
        return "\n\n---\nRelevant memory:\n" + "\n\n".join(snippets)
    except Exception:
        return ""


def _file_to_palace_sync(user: str, human_text: str, ai_reply: str) -> None:
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


# ── MCP tool execution ─────────────────────────────────────────────────────────

async def call_mcp_tool(name: str, args: dict) -> str:
    if mcp_session is None:
        return "MCP not available — cannot execute this action."
    try:
        result = await mcp_session.call_tool(name, args)
        parts = [item.text if hasattr(item, "text") else str(item) for item in result.content]
        return "\n".join(parts) if parts else "Tool returned no output."
    except Exception as e:
        return f"Tool error: {e}"


# ── Core LLM + tool loop ───────────────────────────────────────────────────────

async def ask_diarmuid(user_id: str, text: str) -> str:
    history = conversation_history[user_id]

    memory_context = await asyncio.to_thread(_recall_sync, text)
    augmented_text = f"{text}\n{memory_context}" if memory_context else text
    history.append({"role": "user", "content": augmented_text})

    # Build message list from system prompt + recent history (last 20 turns)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-20:]

    reply = ""
    while True:
        kwargs: dict = {"model": MODEL, "messages": messages}
        if openai_tools:
            kwargs["tools"] = openai_tools

        response = await llm.chat.completions.create(**kwargs)
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            tc_list = choice.message.tool_calls
            # Append assistant message (serialised to dict for the next request)
            messages.append({
                "role": "assistant",
                "content": choice.message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tc_list
                ],
            })
            # Execute each tool and append results
            for tc in tc_list:
                tool_args = json.loads(tc.function.arguments)
                print(f"[MCP] → {tc.function.name}({json.dumps(tool_args)[:120]})")
                result = await call_mcp_tool(tc.function.name, tool_args)
                print(f"[MCP] ← {result[:200]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            reply = choice.message.content or ""
            break

    history.append({"role": "assistant", "content": reply})
    await asyncio.to_thread(_file_to_palace_sync, user_id, text, reply)
    return reply


# ── Slack event handlers ───────────────────────────────────────────────────────

@app.event("app_mention")
async def handle_mention(event, say):
    if event.get("bot_id"):
        return
    user = event.get("user", "unknown")
    text = event.get("text", "")
    reply = await ask_diarmuid(user, text)
    await say(reply)


@app.event("message")
async def handle_message(event, say):
    if event.get("bot_id"):
        return
    if event.get("channel_type", "") != "im":
        return
    user = event.get("user", "unknown")
    text = event.get("text", "")
    reply = await ask_diarmuid(user, text)
    await say(reply)


# ── Startup ────────────────────────────────────────────────────────────────────

async def main():
    global mcp_session, openai_tools

    mcp_binary = pathlib.Path(MCP_BINARY)
    if not mcp_binary.exists():
        print(f"WARNING: github-mcp-server not found at {MCP_BINARY}")
        print("Starting without MCP tools.")
        handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
        await handler.start_async()
        return

    server_params = StdioServerParameters(
        command=str(mcp_binary),
        args=["stdio"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PAT or ""},
    )

    print("Initialising GitHub MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_session = session

            tools_result = await session.list_tools()
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": t.inputSchema,
                    },
                }
                for t in tools_result.tools
            ]
            print(f"MCP ready — {len(openai_tools)} GitHub tools available")
            print("Diarmuid listener starting (Socket Mode + GitHub Models + MCP + MemPalace)...")

            handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
            await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
