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

# ─── Uninstall ──────────────────────────────────────────────────────

if [ "$UNINSTALL" = true ]; then
  echo ""
  echo -e "${BOLD}Uninstalling Astra...${RESET}"
  echo ""

  # Remove Cursor plugin files and JSON registration
  cursor_target="$HOME/.cursor/plugins/astra"
  if [ -d "$cursor_target" ] || [ -L "$cursor_target" ]; then
    rm -rf "$cursor_target"
    ok "Removed Cursor plugin files"
  fi

  if command -v python3 >/dev/null 2>&1; then
    for jsonfile in "$HOME/.claude/plugins/installed_plugins.json" "$HOME/.claude/settings.json"; do
      [ -f "$jsonfile" ] && python3 - "$jsonfile" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path) as f: data = json.load(f)
    data.get("plugins", {}).pop("astra@local", None)
    data.get("enabledPlugins", {}).pop("astra@local", None)
    with open(path, "w") as f: json.dump(data, f, indent=2)
except: pass
PY
    done
    ok "Cursor plugin deregistered"
  fi

  # Remove legacy artifacts
  [ -f "$HOME/.local/bin/claude-astra" ] && rm -f "$HOME/.local/bin/claude-astra" && ok "Removed legacy wrapper"
  for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zprofile" "$HOME/.bash_profile"; do
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
  info "For Claude Code, also run inside any Claude session:"
  echo "    /plugin uninstall astra@local"
  echo ""
  ok "Astra uninstalled."
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

# ─── Step 2: Claude Code ─────────────────────────────────────────────
# Claude Code uses /plugin marketplace — can't be automated from bash.
# The installer downloads the code; the user runs two commands once.

if [ "$HAS_CLAUDE" = true ]; then
  ok "Claude Code: plugin files ready at $ASTRA_DIR"
fi

# ─── Step 3: Cursor ──────────────────────────────────────────────────
# Cursor reads ~/.claude/plugins/installed_plugins.json — can be automated.

if [ "$HAS_CURSOR" = true ]; then
  info "Configuring Cursor..."

  command -v python3 >/dev/null 2>&1 || { warn "python3 required for Cursor setup. Skipping."; }

  if command -v python3 >/dev/null 2>&1; then
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

    # Register in installed_plugins.json
    plugins_json="$HOME/.claude/plugins/installed_plugins.json"
    mkdir -p "$HOME/.claude/plugins"
    python3 - "$plugins_json" "$cursor_target" <<'PY'
import json, os, sys
path, ipath = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path) as f: data = json.load(f)
    except: pass
plugins = data.get("plugins", {})
entries = plugins.get("astra@local", [])
entries = [e for e in entries if not (isinstance(e, dict) and e.get("installPath") == ipath)]
entries.insert(0, {"scope": "user", "installPath": ipath})
plugins["astra@local"] = entries
data["plugins"] = plugins
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f: json.dump(data, f, indent=2)
PY

    # Enable in settings.json
    settings_json="$HOME/.claude/settings.json"
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

    ok "Cursor configured (auto-registered)"
  fi
fi

# ─── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}  Astra installed successfully!${RESET}"
echo ""

if [ "$HAS_CLAUDE" = true ]; then
  echo -e "  ${BOLD}Claude Code (CLI + Desktop + IDE):${RESET}"
  echo ""
  echo "    Run these two commands once inside Claude Code:"
  echo ""
  echo -e "    ${CYAN}/plugin marketplace add $ASTRA_DIR${RESET}"
  echo -e "    ${CYAN}/plugin install astra@local${RESET}"
  echo ""
  echo "    Then in any project:"
  echo "      /astra:setup       (first time per project)"
  echo "      /astra:forge \"feature description\""
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
