#!/usr/bin/env bash
set -euo pipefail

# ─── Astra Installer ────────────────────────────────────────────────
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --cursor
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --claude
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --uninstall
# ─────────────────────────────────────────────────────────────────────

ASTRA_DIR="${ASTRA_DIR:-$HOME/astra}"
REPO_URL="https://github.com/Prateek080/astra.git"

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
  BOLD="\033[1m" DIM="\033[2m" GREEN="\033[32m" YELLOW="\033[33m" RED="\033[31m" CYAN="\033[36m" RESET="\033[0m"
else
  BOLD="" DIM="" GREEN="" YELLOW="" RED="" CYAN="" RESET=""
fi

info()  { echo -e "${BOLD}${CYAN}▸${RESET} $1"; }
ok()    { echo -e "${BOLD}${GREEN}✓${RESET} $1"; }
warn()  { echo -e "${BOLD}${YELLOW}!${RESET} $1"; }
err()   { echo -e "${BOLD}${RED}✗${RESET} $1"; }

# ─── Parse arguments ────────────────────────────────────────────────

FORCE_CLAUDE=false
FORCE_CURSOR=false
UNINSTALL=false
DEV_MODE=false

for arg in "$@"; do
  case "$arg" in
    --claude)    FORCE_CLAUDE=true ;;
    --cursor)    FORCE_CURSOR=true ;;
    --uninstall) UNINSTALL=true ;;
    --dev)       DEV_MODE=true ;;
    --help|-h)
      echo "Astra Installer"
      echo ""
      echo "Usage:"
      echo "  install.sh               Auto-detect editors and install"
      echo "  install.sh --claude      Install for Claude Code only"
      echo "  install.sh --cursor      Install for Cursor only"
      echo "  install.sh --dev         Symlink instead of copy (dev mode)"
      echo "  install.sh --uninstall   Remove Astra from all editors"
      echo ""
      echo "Environment:"
      echo "  ASTRA_DIR   Install location (default: ~/astra)"
      exit 0
      ;;
    *) err "Unknown option: $arg"; exit 1 ;;
  esac
done

# ─── Prerequisites ─────────────────────────────────────────────────

command -v git >/dev/null 2>&1 || { err "git is required. Install it and try again."; exit 1; }
command -v python3 >/dev/null 2>&1 || { err "python3 is required. Install it and try again."; exit 1; }

# ─── Uninstall ──────────────────────────────────────────────────────

if [ "$UNINSTALL" = true ]; then
  echo ""
  echo -e "${BOLD}Uninstalling Astra...${RESET}"
  echo ""

  # Deregister plugin
  local_plugins="$HOME/.claude/plugins/installed_plugins.json"
  local_settings="$HOME/.claude/settings.json"

  if [ -f "$local_plugins" ]; then
    python3 - "$local_plugins" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path) as f: data = json.load(f)
    data.get("plugins", {}).pop("astra@local", None)
    with open(path, "w") as f: json.dump(data, f, indent=2)
except: pass
PY
    ok "Plugin deregistered"
  fi

  if [ -f "$local_settings" ]; then
    python3 - "$local_settings" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path) as f: data = json.load(f)
    data.get("enabledPlugins", {}).pop("astra@local", None)
    with open(path, "w") as f: json.dump(data, f, indent=2)
except: pass
PY
    ok "Plugin disabled"
  fi

  # Remove Cursor plugin files
  cursor_target="$HOME/.cursor/plugins/astra"
  if [ -d "$cursor_target" ] || [ -L "$cursor_target" ]; then
    rm -rf "$cursor_target"
    ok "Removed Cursor plugin files"
  fi

  # Remove legacy wrapper script
  [ -f "$HOME/.local/bin/claude-astra" ] && rm -f "$HOME/.local/bin/claude-astra" && ok "Removed legacy wrapper"

  # Remove legacy shell aliases
  for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zprofile" "$HOME/.bash_profile" "$HOME/.config/fish/config.fish"; do
    if [ -f "$rc" ] && grep -q 'plugin-dir.*astra' "$rc" 2>/dev/null; then
      sed -i.bak '/plugin-dir.*astra/d' "$rc"
      sed -i.bak '/# Astra plugin/d' "$rc"
      rm -f "${rc}.bak"
      ok "Removed legacy alias from $(basename "$rc")"
    fi
  done

  echo ""
  warn "Plugin files at $ASTRA_DIR were NOT removed (you may have local changes)."
  warn "To fully remove: rm -rf $ASTRA_DIR"
  echo ""
  ok "Astra uninstalled. Restart your editor."
  exit 0
fi

# ─── Detect editors ─────────────────────────────────────────────────

detect_claude() {
  command -v claude >/dev/null 2>&1 || [ -d "$HOME/.claude" ]
}

detect_cursor() {
  [ -d "$HOME/.cursor" ] || [ -d "/Applications/Cursor.app" ] || command -v cursor >/dev/null 2>&1
}

HAS_CLAUDE=false
HAS_CURSOR=false

if [ "$FORCE_CLAUDE" = true ]; then
  HAS_CLAUDE=true
elif [ "$FORCE_CURSOR" = true ]; then
  HAS_CURSOR=true
else
  detect_claude && HAS_CLAUDE=true
  detect_cursor && HAS_CURSOR=true
fi

if [ "$HAS_CLAUDE" = false ] && [ "$HAS_CURSOR" = false ]; then
  err "No supported editor detected."
  echo ""
  echo "  Install Claude Code: https://claude.ai/code"
  echo "  Install Cursor:      https://cursor.com"
  echo ""
  echo "  Or specify manually: install.sh --claude  or  install.sh --cursor"
  exit 1
fi

# ─── Header ─────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}  Astra Installer${RESET}"
echo -e "${DIM}  Complete development lifecycle plugin${RESET}"
echo ""

EDITORS=""
[ "$HAS_CLAUDE" = true ] && EDITORS="Claude Code"
[ "$HAS_CURSOR" = true ] && EDITORS="${EDITORS:+$EDITORS + }Cursor"
info "Detected: $EDITORS"
echo ""

# ─── Step 1: Get the code ──────────────────────────────────────────

if [ -d "$ASTRA_DIR/.git" ]; then
  info "Updating Astra at $ASTRA_DIR..."
  git -C "$ASTRA_DIR" pull --quiet 2>/dev/null || warn "Could not pull latest (offline?). Using existing version."
  ok "Astra updated"
else
  info "Cloning Astra to $ASTRA_DIR..."
  git clone --quiet "$REPO_URL" "$ASTRA_DIR"
  ok "Astra cloned"
fi

# ─── Step 2: Register plugin ───────────────────────────────────────
# Same registration for both Claude Code and Cursor — both read
# ~/.claude/plugins/installed_plugins.json and ~/.claude/settings.json

register_plugin() {
  local install_path="$1"
  local plugins_json="$HOME/.claude/plugins/installed_plugins.json"
  local settings_json="$HOME/.claude/settings.json"

  mkdir -p "$HOME/.claude/plugins"

  # Register in installed_plugins.json
  python3 - "$plugins_json" "$install_path" <<'PY'
import json, os, sys
path, ipath = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f: data = json.load(f)
    except: pass
plugins = data.get("plugins", {})
entries = [e for e in plugins.get("astra@local", [])
           if not (isinstance(e, dict) and e.get("scope") == "user")]
entries.insert(0, {"scope": "user", "installPath": ipath})
plugins["astra@local"] = entries
data["plugins"] = plugins
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f: json.dump(data, f, indent=2)
PY

  # Enable in settings.json
  python3 - "$settings_json" <<'PY'
import json, os, sys
path = sys.argv[1]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f: data = json.load(f)
    except: pass
data.setdefault("enabledPlugins", {})["astra@local"] = True
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f: json.dump(data, f, indent=2)
PY

  ok "Plugin registered and enabled"
}

# ─── Step 3: Editor-specific setup ─────────────────────────────────

if [ "$HAS_CLAUDE" = true ]; then
  info "Configuring Claude Code..."
  register_plugin "$ASTRA_DIR"
  ok "Claude Code configured (plugin: $ASTRA_DIR)"
fi

if [ "$HAS_CURSOR" = true ]; then
  info "Configuring Cursor..."

  cursor_target="$HOME/.cursor/plugins/astra"

  if [ "$DEV_MODE" = true ]; then
    rm -rf "$cursor_target"
    mkdir -p "$(dirname "$cursor_target")"
    ln -sf "$ASTRA_DIR" "$cursor_target"
  else
    rm -rf "$cursor_target"
    mkdir -p "$cursor_target"
    for item in .cursor-plugin commands agents skills .mcp.json; do
      [ -e "$ASTRA_DIR/$item" ] && cp -R "$ASTRA_DIR/$item" "$cursor_target/"
    done
  fi

  register_plugin "$cursor_target"
  ok "Cursor configured (plugin: $cursor_target)"
fi

# ─── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}  Astra installed successfully!${RESET}"
echo ""

if [ "$HAS_CLAUDE" = true ]; then
  echo -e "  ${BOLD}Claude Code (CLI, Desktop, IDE extensions):${RESET}"
  echo "    1. Open any project with Claude Code"
  echo "    2. First time? Type: /astra:setup"
  echo "    3. Build anything: /astra:forge \"your feature\""
  echo ""
fi

if [ "$HAS_CURSOR" = true ]; then
  echo -e "  ${BOLD}Cursor:${RESET}"
  echo "    1. Settings > Features > enable 'Include third-party Plugins'"
  echo "    2. Restart Cursor"
  echo "    3. Type / in chat — you should see astra:* commands"
  echo ""
fi

echo -e "  ${DIM}Docs:      https://github.com/Prateek080/astra${RESET}"
echo -e "  ${DIM}Update:    cd ~/astra && git pull && bash install.sh${RESET}"
echo -e "  ${DIM}Uninstall: ~/astra/install.sh --uninstall${RESET}"
echo ""
