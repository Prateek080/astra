# Astra Bootstrap — First-Run Workspace Setup

Run once when initializing an Astra workspace in OpenClaw.

---

## Step 1: Verify Environment

```bash
# Required
command -v python3 || { echo "Python 3.10+ required"; exit 1; }
command -v git || { echo "Git required"; exit 1; }

# Optional but recommended
command -v gh && echo "GitHub CLI available" || echo "Warning: gh CLI not found — PR creation will be manual"
command -v aider && echo "Aider available" || echo "Warning: aider not found — coder agent will use direct exec"
```

---

## Step 2: Install Python Dependencies

```bash
pip install graphifyy pydantic rich pyyaml --quiet
```

Verify:
```bash
python3 -c "import pydantic; import rich; import yaml; print('Dependencies OK')"
python3 -c "import graphifyy; print('Graphify OK')" 2>/dev/null || echo "Warning: graphify not available"
```

---

## Step 3: Build Knowledge Graph

```bash
# Build initial graph (no visualization — faster)
graphify . --no-viz 2>/dev/null || echo "Graphify skipped — agents will scan manually"
```

If the project is large (> 200 files):
```bash
graphify src/ --no-viz  # Scope to primary source directory
```

---

## Step 4: Initialize State Directories

```bash
mkdir -p .astra-state
mkdir -p .astra-cache
mkdir -p docs/.agent-memory
```

Create initial progress file:
```bash
cat > .astra-state/progress.json << 'EOF'
{
  "pipeline_id": null,
  "feature": null,
  "mode": "full",
  "current_stage": "idle",
  "stages": {},
  "started_at": null,
  "completed_at": null
}
EOF
```

Create empty feature queue:
```bash
cat > .astra-state/queue.json << 'EOF'
[]
EOF
```

---

## Step 5: Git Configuration

```bash
# Ensure .gitignore excludes state files
grep -q ".astra-cache/" .gitignore 2>/dev/null || echo ".astra-cache/" >> .gitignore
grep -q ".astra-state/" .gitignore 2>/dev/null || echo ".astra-state/" >> .gitignore
grep -q "graphify-out/" .gitignore 2>/dev/null || echo "graphify-out/" >> .gitignore
grep -q "docs/.agent-memory/" .gitignore 2>/dev/null || echo "docs/.agent-memory/" >> .gitignore
```

---

## Step 6: Verify Shared Code

The Astra orchestrator checks (S1-S5, D1-D5, P1-P4, T1-T5, I1-I4) are reused from the Claude Code version. Verify they're accessible:

```bash
python3 -c "
import sys
sys.path.insert(0, '${ASTRA_PLUGIN_DIR:-~/astra}')
from orchestrator.checks.base import CheckStatus, StageGateResult
print('Stage-gate checks: OK')
" || echo "Warning: orchestrator checks not found — run_stage_eval.py will need standalone checks"
```

---

## Step 7: Configure Reporting (Optional)

If Telegram reporting is configured in plugin settings:
```bash
python3 scripts/report.py --dry-run --channel telegram --event start --stage bootstrap --details "Workspace initialized"
```

If Discord:
```bash
python3 scripts/report.py --dry-run --channel discord --event start --stage bootstrap --details "Workspace initialized"
```

---

## Verification

All checks must pass:
```bash
echo "=== Bootstrap Verification ==="
[ -d .astra-state ] && echo "✓ State directory" || echo "✗ State directory missing"
[ -f .astra-state/progress.json ] && echo "✓ Progress file" || echo "✗ Progress file missing"
[ -f .astra-state/queue.json ] && echo "✓ Queue file" || echo "✗ Queue file missing"
[ -d .astra-cache ] && echo "✓ Cache directory" || echo "✗ Cache directory missing"
[ -d docs/.agent-memory ] && echo "✓ Memory directory" || echo "✗ Memory directory missing"
python3 -c "import pydantic; import rich; import yaml" 2>/dev/null && echo "✓ Python deps" || echo "✗ Python deps missing"
echo "=== Bootstrap Complete ==="
```

---

## What This Creates

| Path | Purpose | Gitignored? |
|------|---------|-------------|
| `.astra-state/` | Pipeline state (progress.json, queue.json, forge-state.json) | Yes |
| `.astra-cache/` | Temporary caches (context.md, audit.jsonl) | Yes |
| `docs/.agent-memory/` | Agent cross-session learnings | Yes |
| `graphify-out/` | Knowledge graph output | Yes |
