#!/bin/bash
# Hook: SubagentStart — remind subagents to read context sources.
# Checks graphify-out/GRAPH_REPORT.md first, falls back to .astra-cache/context.md.

GRAPH_REPORT="graphify-out/GRAPH_REPORT.md"
CACHE_FILE=".astra-cache/context.md"

if [ -f "$GRAPH_REPORT" ]; then
    cat <<'HOOKJSON'
{
  "systemMessage": "IMPORTANT: Read graphify-out/GRAPH_REPORT.md for codebase context (knowledge graph with community clusters, god nodes, and connectivity patterns). For targeted lookups, use `/graphify query \"topic\"` or `/graphify path \"A\" \"B\"`. Do not re-scan the codebase independently."
}
HOOKJSON
elif [ -f "$CACHE_FILE" ]; then
    cat <<'HOOKJSON'
{
  "systemMessage": "IMPORTANT: Read .astra-cache/context.md for codebase context before starting. Do not re-scan the codebase independently."
}
HOOKJSON
else
    echo '{}'
fi
