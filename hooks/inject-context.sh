#!/bin/bash
# Hook: SubagentStart — remind subagents to use graphify query-first for context.
# Priority: /graphify query (targeted) → GRAPH_REPORT.md (full) → context.md (flat scan).

GRAPH_REPORT="graphify-out/GRAPH_REPORT.md"
CACHE_FILE=".astra-cache/context.md"

if [ -f "$GRAPH_REPORT" ]; then
    cat <<'HOOKJSON'
{
  "systemMessage": "IMPORTANT: Use `/graphify query \"topic\"` or `/graphify path \"A\" \"B\"` for targeted codebase context first. Only read graphify-out/GRAPH_REPORT.md if query returns insufficient results. Do not re-scan the codebase independently."
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
