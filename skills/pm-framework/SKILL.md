---
name: pm-framework
description: PRD methodology for producing agent-consumable specifications with numbered, testable requirements
user-invocable: false
---

# PM Framework

This skill defines how to produce agent-consumable product specifications. Every spec you write must follow this methodology exactly.

## 1. Pre-Draft Questioning

Before writing a single line of spec, ask 3-5 clarifying questions. These questions must be **specific to the feature described** -- not generic PM boilerplate.

**Focus areas:**

1. **Core problem**: What is the user struggling with today? Restate what you think the problem is and ask if that framing is correct. The user often describes a solution -- dig for the underlying problem.
2. **Affected users**: Which specific user segments hit this pain? How frequently? What are they doing instead right now (workaround)?
3. **Definition of done**: What measurable outcome signals success? "It works" is not an answer. Push for a number: conversion rate, time saved, error rate reduced, adoption percentage.
4. **Scope boundaries**: What is explicitly NOT part of this work? Name at least one adjacent feature or edge case you suspect the user might assume is included.
5. **Constraints**: Existing integrations this must respect, known tech debt that complicates this area, hard deadlines, compliance requirements.

**Anti-patterns -- do not do these:**

- Do NOT ask "what tech stack?" -- read CLAUDE.md and the codebase for that.
- Do NOT ask 10+ shallow questions. Ask 5 deep ones that force the user to think.
- Do NOT ask questions whose answers are already in PRODUCT.md or prior specs.
- Do NOT ask "who is the target user?" generically. Name a hypothesis: "I think this primarily affects admin users managing teams of 10+. Is that right, or is the audience broader?"

## 2. Spec Methodology -- Compressed 8-Phase PRD

Based on structured product management practice, adapted for agent consumption.

### Phase 1: Executive Summary

One sentence using this template:

> We are building **[solution]** for **[persona]** to solve **[problem]**, resulting in **[measurable impact]**.

If you cannot fill every bracket with specifics, you are not ready to write the spec. Go back to questioning.

### Phase 2: Problem Statement

State the problem concretely with evidence:

- User complaints, support tickets, or observed friction
- Current metrics that are underperforming
- Workflow steps that are manual, error-prone, or slow

Must answer: **"What happens if we do nothing?"** If the answer is "nothing bad," challenge whether this feature should be built at all.

### Phase 3: Personas

1-3 minimal personas. Only include personas that **change the requirements** -- if two personas need the same thing, merge them.

Format per persona:
- **Name** (Role): Goal. Pain: [specific pain point that this feature addresses].

### Phase 4: Strategy & Scope

Use the Now / Next / Later framework:

- **Now (this iteration):** What we are building and shipping. Be precise.
- **Next (likely follow-up):** What we are explicitly deferring but acknowledge as probable.
- **Later (maybe never):** Adjacent ideas that came up but are out of scope.

This section prevents scope creep. If a requirement does not appear under "Now," it does not get an R-number.

### Phase 5: Solution Requirements

This is the core of the spec. Every requirement gets a stable ID.

Format per requirement:

```
### R[n]: [Requirement title]
[One-line description of what the system must do]
**RICE:** [score] (R:[1-10] I:[0.25|0.5|1|2|3] C:[100%|80%|50%] E:[person-months])
**Dependencies:** [R{n}, R{n} | none]
**Acceptance criteria:**
- Given [context], when [action], then [expected result]
- Given [context], when [edge case], then [expected handling]
```

See **Section 4: RICE Scoring Guide** for scale definitions and formula.

**Rules for writing requirements:**

- Order by RICE score descending (highest priority first).
- Each requirement must be independently testable. If you cannot write a test for it, rewrite it.
- One requirement = one capability. If a requirement has "and" in it, split it.
- Acceptance criteria use Given/When/Then so the reviewer agent can verify them against code.

### Phase 6: Non-Functional Requirements

These must have **concrete numbers**, not aspirations:

- **Performance:** Response time targets at specific percentiles (e.g., p95 < 200ms). Throughput targets. Payload size limits.
- **Security:** Authentication method, authorization model, data encryption requirements, audit logging.
- **Accessibility:** WCAG conformance level (A, AA, or AAA) and any specific needs (screen reader support, keyboard navigation, color contrast ratios).
- **Compatibility:** Supported browsers, devices, screen sizes, API versions.

### Phase 7: Success Metrics

At minimum, one leading and one lagging metric:

- **Leading metric:** An early signal that the feature is working (e.g., adoption rate in first week, task completion rate, click-through rate).
- **Lagging metric:** A longer-term confirmation of value (e.g., retention impact after 30 days, support ticket reduction over a quarter, revenue impact).

### Phase 8: Open Questions

Unresolved items that could affect design or implementation. Each must state:
- The question itself
- Why it matters (what changes depending on the answer)
- Who can answer it or what research is needed

## 3. Agent-Consumable Requirements Rules

This section defines what makes a spec usable by downstream agents (planner, implementer, reviewer). A human-readable PRD is not enough -- the spec must be machine-parseable.

### Stable IDs

Every requirement gets `R1`, `R2`, `R3`, etc. These IDs persist through the entire pipeline: spec, plan, implementation, review. When the reviewer agent checks acceptance criteria, it references `R1` directly.

### No Vague Language

Vague terms are banned. Use this translation table:

| Banned term | Replace with |
|---|---|
| "fast" | "responds within 200ms at p95" |
| "intuitive" | "completes task in under 3 clicks with no prior training" |
| "secure" | specific auth/authz requirements (e.g., "requires JWT with role-based access") |
| "scalable" | "handles 10k concurrent users with < 1% error rate" |
| "user-friendly" | specific usability criteria (e.g., "form validates inline before submission") |
| "seamless" | "zero manual steps between [action A] and [action B]" |
| "robust" | specific error handling (e.g., "retries 3x with exponential backoff on network failure") |
| "flexible" | specific extension points (e.g., "supports custom validators via plugin interface") |

If you catch yourself writing a vague term, stop and replace it before continuing.

### Given/When/Then Format

Every acceptance criterion follows this structure so agents can parse and verify them:

```
Given [a specific precondition or system state],
when [the user or system performs an action],
then [a specific, observable, testable outcome occurs].
```

Bad: "The user can delete items." Good: "Given a user viewing their item list with 3 items, when they click delete on the second item, then the list shows 2 items and a success toast appears within 500ms."

### Independently Testable

Each requirement must be verifiable in isolation. If testing R3 requires R1 and R2 to be implemented first, document that dependency explicitly: "R3 depends on R1."

## 4. RICE Scoring Guide

Score every functional requirement to establish priority order.

| Factor | What it measures | Scale |
|---|---|---|
| **Reach** | Users affected per quarter | 1-10 (1 = handful, 10 = all users) |
| **Impact** | Improvement per user | 0.25 = minimal, 0.5 = low, 1 = medium, 2 = high, 3 = massive |
| **Confidence** | Certainty of estimates | 100% = high (data-backed), 80% = medium (informed guess), 50% = low (speculation) |
| **Effort** | Person-months of work | Lower effort = higher priority |

**Formula:** `Score = (Reach x Impact x Confidence) / Effort`

**Example:** A feature reaching 8/10 users, with high impact (2), medium confidence (80%), taking 2 person-months: `(8 x 2 x 0.8) / 2 = 6.4`

When confidence is 50% or below, flag the requirement in Open Questions -- it needs research before committing.

## 5. SPEC.md Output Template

Write the final spec to `SPEC.md` in the project root. Use this exact structure:

```markdown
# Feature: [Name]

## Executive Summary
We are building [solution] for [persona] to solve [problem], resulting in [impact].

## Problem
[Concrete problem statement with evidence. What happens if we do nothing?]

## Personas
- **[Name]** ([Role]): [Goal]. Pain: [specific pain point].

## Scope

### Now (this spec)
[What we are building and shipping in this iteration. Be precise.]

### Next (future)
[What we are explicitly deferring but acknowledge as probable follow-up work.]

### Later (aspirational)
[Adjacent ideas that came up but are out of scope. May never be built.]

## Requirements

### R1: [Requirement title]
[One-line description]
**RICE:** [score] (R:[1-10] I:[0.25|0.5|1|2|3] C:[100%|80%|50%] E:[person-months])
**Dependencies:** [R{n}, R{n} | none]
**Acceptance criteria:**
- Given [context], when [action], then [expected result]
- Given [context], when [edge case], then [expected handling]

### R2: [Requirement title]
...

## Non-Functional Requirements
- Performance: [specific targets with numbers]
- Security: [specific requirements]
- Accessibility: [WCAG level and specific needs]

## Success Metrics
- Leading: [metric that indicates early progress]
- Lagging: [metric that confirms long-term success]

## Open Questions
- [Question that could affect design or implementation]
```

## 6. Incremental Feature Rules

When PRODUCT.md already exists (this is not the first feature for the project):

1. **Read first:** Read all existing features and the design system in PRODUCT.md before asking clarifying questions. Your questions should demonstrate awareness of what already exists.
2. **Delta requirements:** Frame requirements as additions to the existing system. Write "Add X to existing Y" not "Build Y from scratch." If the system already has a navigation bar, your requirement is "Add a settings link to the navigation bar," not "Create a navigation bar with a settings link."
3. **Integration points:** Explicitly call out where the new feature touches existing features. Example: "R3 adds a filter to the existing search component (see Feature: Search, R2)."
4. **No re-specification:** Do not re-specify existing functionality. Reference it: "Uses the existing authentication flow (Feature: Auth, R1-R4)."
5. **Modification markers:** If a new requirement changes existing behavior, mark it clearly: `MODIFIES R[existing-id]` with an explanation of what changes and why.
6. **Backward compatibility:** State whether existing tests should continue to pass as-is, or whether specific tests need updating (and why).

## 7. Revision Protocol

When the user provides feedback on an existing spec, update the spec **in-place**. Do not rewrite from scratch.

**Rules:**

1. **Preserve requirement IDs.** Existing requirements keep their `R{n}` IDs, even if their content changes. Never renumber existing requirements.
2. **Append new requirements.** New requirements get the next available ID. If the spec has R1-R5 and feedback adds two requirements, they become R6 and R7.
3. **Mark deleted requirements.** If feedback removes a requirement, mark it `[REMOVED]` rather than deleting the entry. This keeps the ID sequence stable for any downstream references (plans, code comments, test names).
4. **Update RICE scores.** If scope or understanding changed, re-score affected requirements and re-sort by score.
5. **Track changes briefly.** At the top of the spec, add or update a `**Last revised:** [date] -- [one-line summary of what changed]` line so reviewers can see the revision history at a glance.
