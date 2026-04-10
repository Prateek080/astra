---
name: retrospective
description: Assess how the last feature went and suggest workflow improvements
user-invocable: true
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash
---

# Retrospective

Review the recent development work and assess what went well, what didn't, and what to improve.

## Analysis

1. **Read artifacts**: Look for SPEC.md, DESIGN.md, PLAN.md, PRODUCT.md, and recent git history (`git log --oneline -20`). Also check `docs/specs/`, `docs/designs/`, and `docs/plans/` for archived versions.

2. **Plan vs Reality**:
   - Did the plan match what was actually implemented?
   - Were there phases that took longer or were more complex than estimated?
   - Were there unplanned changes (scope creep, unexpected dependencies)?

3. **Quality Assessment**:
   - Were there bugs found after implementation that the review should have caught?
   - Were tests adequate? Any areas with poor coverage?
   - Were there any reverts or hotfixes?

4. **Process Assessment**:
   - Was the spec detailed enough, or were there too many open questions during implementation?
   - Was the plan structured well, or did phases need re-ordering?
   - Did the research phase catch potential blockers, or were there surprises?

5. **Reusability Assessment**:
   - Was new code written that duplicates existing patterns?
   - Were utilities created that could benefit other parts of the codebase?
   - Are there new shared patterns worth documenting?

## Output

``````markdown
# Retrospective — [Feature Name] — [Date]

## What Went Well
- [Specific positive]

## What Didn't Go Well
- [Specific issue]

## Suggested Improvements

### For review-checklist skill (add these checks):
```markdown
[Copy-pasteable checklist items to add]
```

### For plan-template skill (structural improvements):
```markdown
[Copy-pasteable improvements]
```

### For project CLAUDE.md (new conventions):
```markdown
[Copy-pasteable rules discovered during this feature]
```

### For .claude/rules/ and .cursor/rules/ (path-specific rules):
```markdown
[Any file-type-specific rules discovered]
```
``````

Format all suggestions as copy-pasteable markdown blocks so the user can add them directly to the relevant files.
