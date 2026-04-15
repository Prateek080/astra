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

# ─── Uninstall ──────────────────────────────────────────────────────

uninstall_claude() {
  info "Removing Claude Code configuration..."

  # Remove shell alias
  for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.config/fish/config.fish"; do
    if [ -f "$rc" ]; then
      if grep -q 'plugin-dir.*astra' "$rc" 2>/dev/null; then
        sed -i.bak '/plugin-dir.*astra/d' "$rc"
        rm -f "${rc}.bak"
        ok "Removed alias from $(basename "$rc")"
      fi
    fi
  done

  ok "Claude Code configuration removed"
}

uninstall_cursor() {
  info "Removing Cursor configuration..."

  local target="$HOME/.cursor/plugins/astra"
  local plugins_json="$HOME/.claude/plugins/installed_plugins.json"
  local settings_json="$HOME/.claude/settings.json"

  # Remove plugin directory
  if [ -d "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
    ok "Removed plugin files"
  fi

  # Deregister from installed_plugins.json
  if [ -f "$plugins_json" ] && command -v python3 >/dev/null 2>&1; then
    python3 - "$plugins_json" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path) as f: data = json.load(f)
    data.get("plugins", {}).pop("astra@local", None)
    with open(path, "w") as f: json.dump(data, f, indent=2)
except: pass
PY
  fi

  # Disable in settings.json
  if [ -f "$settings_json" ] && command -v python3 >/dev/null 2>&1; then
    python3 - "$settings_json" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path) as f: data = json.load(f)
    data.get("enabledPlugins", {}).pop("astra@local", None)
    with open(path, "w") as f: json.dump(data, f, indent=2)
except: pass
PY
  fi

  ok "Cursor configuration removed"
}

if [ "$UNINSTALL" = true ]; then
  echo ""
  echo -e "${BOLD}Uninstalling Astra...${RESET}"
  echo ""

  uninstall_claude
  uninstall_cursor

  echo ""
  warn "Plugin files at $ASTRA_DIR were NOT removed (you may have local changes)."
  warn "To fully remove: rm -rf $ASTRA_DIR"
  echo ""
  ok "Astra uninstalled. Restart your editor to complete removal."
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
  command -v git >/dev/null 2>&1 || { err "git is required. Install it and try again."; exit 1; }
  git clone --quiet "$REPO_URL" "$ASTRA_DIR"
  ok "Astra cloned"
fi

# ─── Step 2: Install for Claude Code ───────────────────────────────

install_claude() {
  info "Configuring Claude Code..."

  local shell_rc="" is_fish=false

  # Step 1: Detect shell from $SHELL
  case "${SHELL:-}" in
    */zsh)  shell_rc="$HOME/.zshrc" ;;
    */bash) shell_rc="$HOME/.bashrc" ;;
    */fish) shell_rc="$HOME/.config/fish/config.fish"; is_fish=true ;;
  esac

  # Step 2: If detected file doesn't exist, try common alternatives
  if [ -n "$shell_rc" ] && [ ! -f "$shell_rc" ]; then
    case "${SHELL:-}" in
      */zsh)
        for alt in "$HOME/.zprofile" "$HOME/.profile"; do
          [ -f "$alt" ] && shell_rc="$alt" && break
        done
        ;;
      */bash)
        for alt in "$HOME/.bash_profile" "$HOME/.profile"; do
          [ -f "$alt" ] && shell_rc="$alt" && break
        done
        ;;
    esac
  fi

  # Step 3: If $SHELL not set, probe for existing rc files
  if [ -z "$shell_rc" ]; then
    for candidate in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.zprofile" "$HOME/.bash_profile" "$HOME/.profile"; do
      [ -f "$candidate" ] && shell_rc="$candidate" && break
    done
  fi

  # Step 4: Still nothing — create the appropriate rc file for the detected shell
  if [ -z "$shell_rc" ]; then
    case "${SHELL:-}" in
      */zsh)  shell_rc="$HOME/.zshrc" ;;
      */bash) shell_rc="$HOME/.bashrc" ;;
      */fish) shell_rc="$HOME/.config/fish/config.fish"; is_fish=true ;;
      *)      shell_rc="$HOME/.profile" ;;  # POSIX fallback
    esac
    info "Creating $(basename "$shell_rc") (no existing shell config found)"
  fi

  # Ensure parent directory exists (needed for fish)
  mkdir -p "$(dirname "$shell_rc")"

  # Build alias line (fish uses different syntax)
  local alias_line
  if [ "$is_fish" = true ]; then
    alias_line="alias claude \"claude --plugin-dir $ASTRA_DIR\""
  else
    alias_line="alias claude=\"claude --plugin-dir $ASTRA_DIR\""
  fi

  # Check if already configured
  if grep -q 'plugin-dir.*astra' "$shell_rc" 2>/dev/null; then
    ok "Claude Code already configured in $(basename "$shell_rc")"
  else
    echo "" >> "$shell_rc"
    echo "# Astra plugin" >> "$shell_rc"
    echo "$alias_line" >> "$shell_rc"
    ok "Added alias to $(basename "$shell_rc")"
  fi
}

if [ "$HAS_CLAUDE" = true ]; then
  install_claude
fi

# ─── Step 3: Install for Cursor ────────────────────────────────────

install_cursor() {
  info "Configuring Cursor..."

  command -v python3 >/dev/null 2>&1 || { warn "python3 required for Cursor setup. Skipping."; return; }

  local target="$HOME/.cursor/plugins/astra"
  local plugins_json="$HOME/.claude/plugins/installed_plugins.json"
  local settings_json="$HOME/.claude/settings.json"

  # Copy or symlink plugin files
  local components=(.cursor-plugin commands agents skills .mcp.json)

  if [ "$DEV_MODE" = true ]; then
    rm -rf "$target"
    mkdir -p "$(dirname "$target")"
    ln -sf "$ASTRA_DIR" "$target"
  else
    rm -rf "$target"
    mkdir -p "$target"
    for item in "${components[@]}"; do
      if [ -e "$ASTRA_DIR/$item" ]; then
        cp -R "$ASTRA_DIR/$item" "$target/"
      fi
    done
  fi

  # Register plugin
  mkdir -p "$HOME/.claude/plugins"
  python3 - "$plugins_json" "$target" <<'PY'
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

  # Enable plugin
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

  ok "Cursor configured"
}

if [ "$HAS_CURSOR" = true ]; then
  install_cursor
fi

# ─── Step 4: Install Python orchestrator (optional) ────────────────

install_orchestrator() {
  if ! command -v python3 >/dev/null 2>&1; then
    warn "Python 3 not found. SDK orchestrator (astra-forge) will not be available."
    warn "The markdown-based /astra:forge still works without Python."
    return
  fi

  PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

  if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    warn "Python $PY_VERSION found, but 3.10+ required for the SDK orchestrator."
    return
  fi

  info "Setting up Python orchestrator (astra-forge)..."

  if command -v pipx >/dev/null 2>&1; then
    pipx install "$ASTRA_DIR" --force --quiet 2>/dev/null && ok "Installed astra-forge via pipx" || {
      # Fallback to pip if pipx fails
      python3 -m pip install --user "$ASTRA_DIR" --quiet 2>/dev/null && ok "Installed astra-forge via pip" || \
        warn "Could not install astra-forge. Install manually: pip install $ASTRA_DIR"
    }
  else
    python3 -m pip install --user "$ASTRA_DIR" --quiet --break-system-packages 2>/dev/null && ok "Installed astra-forge via pip" || {
      python3 -m pip install --user "$ASTRA_DIR" --quiet 2>/dev/null && ok "Installed astra-forge via pip" || \
        warn "Could not install astra-forge. Install manually: pip install $ASTRA_DIR"
    }
  fi

  # Check token configuration
  if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    info "Note: Set ANTHROPIC_API_KEY for the SDK orchestrator"
  fi
  if [ -z "${GITHUB_TOKEN:-}" ]; then
    info "Note: Set GITHUB_TOKEN for GitHub MCP integration (optional)"
  fi
  if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
    info "Note: Set SLACK_WEBHOOK_URL for Slack notifications (optional)"
  fi
}

install_orchestrator

# ─── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}  Astra installed successfully!${RESET}"
echo ""

if [ "$HAS_CLAUDE" = true ]; then
  echo -e "  ${BOLD}Claude Code:${RESET}"
  echo "    1. Restart your terminal (or run: source ~/.zshrc)"
  echo "    2. Open any project: claude"
  echo "    3. Run: /astra:setup"
  echo ""
fi

if [ "$HAS_CURSOR" = true ]; then
  echo -e "  ${BOLD}Cursor:${RESET}"
  echo "    1. Settings > Features > enable 'Include third-party Plugins'"
  echo "    2. Restart Cursor"
  echo "    3. Type / in chat — you should see astra:* commands"
  echo ""
fi

if command -v astra-forge >/dev/null 2>&1; then
  echo -e "  ${BOLD}SDK Orchestrator:${RESET}"
  echo "    astra-forge \"feature description\"    # Full autonomous pipeline"
  echo "    astra-forge schedule list             # Manage scheduled tasks"
  echo ""
fi

echo -e "  ${DIM}Docs: https://github.com/Prateek080/astra${RESET}"
echo -e "  ${DIM}Update: cd ~/astra && git pull && pip install ~/astra${RESET}"
echo -e "  ${DIM}Uninstall: ~/astra/install.sh --uninstall${RESET}"
echo ""
