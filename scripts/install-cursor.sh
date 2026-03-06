#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null || { echo "Error: python3 is required but not found."; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_NAME="astra"
PLUGIN_ID="${PLUGIN_NAME}@local"
TARGET="$HOME/.cursor/plugins/$PLUGIN_NAME"
CLAUDE_PLUGINS="$HOME/.claude/plugins/installed_plugins.json"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
DEV_MODE=false
UNINSTALL=false

for arg in "$@"; do
  case "$arg" in
    --dev) DEV_MODE=true ;;
    --uninstall) UNINSTALL=true ;;
    --help|-h)
      echo "Usage: install-cursor.sh [--dev] [--uninstall]"
      echo ""
      echo "Install or remove the Astra plugin for Cursor IDE."
      echo ""
      echo "Options:"
      echo "  --dev        Symlink instead of copy (changes reflect without re-running)"
      echo "  --uninstall  Remove Astra plugin and deregister from settings"
      echo ""
      exit 0
      ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

if [ "$UNINSTALL" = true ]; then
  echo "Uninstalling Astra plugin from Cursor..."
  echo ""

  echo "[1/3] Removing plugin files"
  rm -rf "$TARGET"

  echo "[2/3] Deregistering plugin"
  python3 - "$CLAUDE_PLUGINS" "$PLUGIN_ID" <<'PY'
import json, os, sys

path, pid = sys.argv[1], sys.argv[2]
if not os.path.exists(path):
    sys.exit(0)
try:
    with open(path) as f:
        data = json.load(f)
except (json.JSONDecodeError, IOError):
    sys.exit(0)

plugins = data.get("plugins", {})
plugins.pop(pid, None)
data["plugins"] = plugins

with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY

  echo "[3/3] Disabling plugin"
  python3 - "$CLAUDE_SETTINGS" "$PLUGIN_ID" <<'PY'
import json, os, sys

path, pid = sys.argv[1], sys.argv[2]
if not os.path.exists(path):
    sys.exit(0)
try:
    with open(path) as f:
        data = json.load(f)
except (json.JSONDecodeError, IOError):
    sys.exit(0)

data.get("enabledPlugins", {}).pop(pid, None)

with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY

  echo ""
  echo "Astra has been removed. Restart Cursor to complete the uninstall."
  exit 0
fi

echo "Installing Astra plugin for Cursor..."
echo ""

# Step 1: Copy (or symlink) plugin files
COMPONENTS=(.cursor-plugin commands agents skills .mcp.json)

if [ "$DEV_MODE" = true ]; then
  echo "[1/3] Symlinking plugin to $TARGET (dev mode)"
  rm -rf "$TARGET"
  mkdir -p "$(dirname "$TARGET")"
  ln -sf "$REPO_ROOT" "$TARGET"
else
  echo "[1/3] Copying plugin to $TARGET"
  rm -rf "$TARGET"
  mkdir -p "$TARGET"
  for item in "${COMPONENTS[@]}"; do
    if [ -e "$REPO_ROOT/$item" ]; then
      cp -R "$REPO_ROOT/$item" "$TARGET/"
    fi
  done
fi

# Step 2: Register in ~/.claude/plugins/installed_plugins.json
echo "[2/3] Registering plugin"
mkdir -p "$HOME/.claude/plugins"

python3 - "$CLAUDE_PLUGINS" "$PLUGIN_ID" "$TARGET" <<'PY'
import json, os, sys

path, pid, ipath = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {}

plugins = data.get("plugins", {})
entries = [e for e in plugins.get(pid, [])
           if not (isinstance(e, dict) and e.get("scope") == "user")]
entries.insert(0, {"scope": "user", "installPath": ipath})
plugins[pid] = entries
data["plugins"] = plugins

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY

# Step 3: Enable in ~/.claude/settings.json
echo "[3/3] Enabling plugin"

python3 - "$CLAUDE_SETTINGS" "$PLUGIN_ID" <<'PY'
import json, os, sys

path, pid = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {}

data.setdefault("enabledPlugins", {})[pid] = True

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY

echo ""
echo "Done! Next steps:"
echo ""
echo "  1. In Cursor: Settings > Features > enable 'Include third-party Plugins, Skills, and other configs'"
echo "  2. Restart Cursor (Cmd+Q then reopen, or Cmd+Shift+P > 'Reload Window')"
echo "  3. Type / in chat — you should see astra:* commands"
echo ""
if [ "$DEV_MODE" = true ]; then
  echo "Dev mode: plugin is symlinked. Edits to $REPO_ROOT are reflected immediately (restart Cursor to pick up changes)."
else
  echo "To update after pulling changes: run this script again."
fi
