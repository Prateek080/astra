---
name: pm-framework
description: PRD methodology for producing agent-consumable specifications with numbered, testable requirements
user-invocable: false
---

# PM Framework

Methodology for agent-consumable product specs. Follow exactly.

## 1. Pre-Draft Questioning

Ask 3-5 clarifying questions **specific to the feature** before writing:

1. **Core problem:** Restate the problem you infer and ask if correct. Dig past solutions to find the underlying pain.
2. **Affected users:** Which segments, how frequently, current workarounds?
3. **Definition of done:** Measurable outcome — push for a number (conversion rate, time saved, error rate).
4. **Scope boundaries:** What is explicitly NOT included? Name at least one adjacent feature.
5. **Constraints:** Existing integrations, tech debt, deadlines, compliance.

**Don't:** Ask "what tech stack?" (read CLAUDE.md). Ask 10+ shallow questions. Ask questions answered by PRODUCT.md.
**Do:** State hypotheses: "I think this affects admin users managing teams of 10+. Correct?"

## 2. Compressed 8-Phase PRD

### Phase 1: Executive Summary
> We are building **[solution]** for **[persona]** to solve **[problem]**, resulting in **[measurable impact]**.

### Phase 2: Problem Statement
Concrete problem with evidence. Must answer: "What happens if we do nothing?"

### Phase 3: Personas
1-3 personas that **change requirements**. Format: **Name** (Role): Goal. Pain: [specific pain].

### Phase 4: Scope — Now / Next / Later
- **Now:** What we build this iteration. Only "Now" items get R-numbers.
- **Next:** Explicitly deferred but probable.
- **Later:** Out of scope, maybe never.

### Phase 5: Requirements
```
### R[n]: [Title]
[One-line description]
**RICE:** [score] (R:[1-10] I:[0.25|0.5|1|2|3] C:[100%|80%|50%] E:[person-months])
**Dependencies:** [R{n} | none]
**Acceptance criteria:**
- Given [context], when [action], then [result]
- Given [context], when [edge case], then [handling]
```
Order by RICE descending. One requirement = one capability (split if "and"). Each must be independently testable.

### Phase 6: Non-Functional Requirements
Concrete numbers only: p95 < 200ms, WCAG AA, specific auth method, supported browsers.

### Phase 7: Success Metrics
One leading metric (early signal) + one lagging metric (long-term confirmation).

### Phase 8: Open Questions
Unresolved items: the question, why it matters, who can answer it.

## 3. Agent-Consumable Rules

- **Stable IDs:** R1, R2, R3... persist through entire pipeline (spec → plan → code → review).
- **No vague language:** "fast" → "p95 < 200ms". "intuitive" → "completes in < 3 clicks". "secure" → "JWT with RBAC". "scalable" → "10k concurrent, < 1% errors".
- **Given/When/Then:** Every acceptance criterion follows this format for machine parsing.
- **Independently testable:** If R3 requires R1, document: "R3 depends on R1."

## 4. RICE Scoring

| Factor | Scale |
|---|---|
| **Reach** | 1-10 (users affected per quarter) |
| **Impact** | 0.25 minimal, 0.5 low, 1 medium, 2 high, 3 massive |
| **Confidence** | 100% data-backed, 80% informed guess, 50% speculation |
| **Effort** | Person-months (lower = higher priority) |

**Formula:** `(Reach × Impact × Confidence) / Effort`

Flag requirements with ≤50% confidence in Open Questions.

## 5. SPEC.md Output Template

```markdown
# Feature: [Name]

## Executive Summary
We are building [solution] for [persona] to solve [problem], resulting in [impact].

## Problem
[Concrete with evidence. What happens if we do nothing?]

## Personas
- **[Name]** ([Role]): [Goal]. Pain: [pain].

## Scope
### Now (this spec)
### Next (future)
### Later (aspirational)

## Requirements
### R1: [Title]
[Description]
**RICE:** [score] (R:[] I:[] C:[] E:[])
**Dependencies:** [none]
**Acceptance criteria:**
- Given [], when [], then []

## Non-Functional Requirements
## Success Metrics
## Open Questions
```

## 6. Incremental Feature Rules

When PRODUCT.md exists: read existing features first. Frame as deltas ("Add X to existing Y"). Reference existing functionality, don't re-specify. Mark modifications: `MODIFIES R[existing-id]`.

## 7. Revision Protocol

Update in-place, never rewrite from scratch:
1. Preserve existing R{n} IDs — never renumber.
2. Append new requirements as next available ID.
3. Mark removed requirements `[REMOVED]` — keep ID stable.
4. Re-score affected RICE scores.
5. Add `**Last revised:** [date] — [summary]` at top.
