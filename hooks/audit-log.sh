#!/bin/bash
# Hook: PostToolUse — append tool call info to audit log.
# Reads hook input from stdin, extracts tool name and file path.

AUDIT_FILE=".astra-cache/audit.jsonl"
mkdir -p "$(dirname "$AUDIT_FILE")"

# Read stdin (hook input JSON)
INPUT=$(cat)

# Extract tool name
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")

# Extract file path if present
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Write audit entry
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL\",\"file_path\":\"$FILE_PATH\"}" >> "$AUDIT_FILE"

# Return empty response (don't modify behavior)
echo '{}'
