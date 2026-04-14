#!/bin/bash
# Hook: SubagentStart — remind subagents to read the context cache.
# Outputs JSON that Claude Code injects as a system message.

CACHE_FILE=".astra-cache/context.md"

if [ -f "$CACHE_FILE" ]; then
    cat <<'HOOKJSON'
{
  "systemMessage": "IMPORTANT: Read .astra-cache/context.md for codebase context before starting. Do not re-scan the codebase independently."
}
HOOKJSON
else
    echo '{}'
fi
