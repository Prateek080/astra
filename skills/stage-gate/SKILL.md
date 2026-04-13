---
name: stage-gate
description: Automated eval gates between forge pipeline stages — checks artifact quality, proceeds or stops
user-invocable: false
---

# Stage Gate Eval

Run after each forge stage. Score every check as **pass/warn/fail**. Decision logic:

| Result | Action |
|---|---|
| All pass | Print `✓` line, proceed |
| Warnings only | Auto-fix once, print `⚠` line, proceed |
| Any fail | Auto-fix once, re-eval. Still fail → **STOP**, show user |

Print format: `[✓/⚠/✗] [Stage]: [summary] | [check1] ✓ | [check2] ⚠ reason | ...`

---

## SPEC Eval

Run after PM agent writes SPEC.md.

| # | Check | Pass | Warn | Fail |
|---|---|---|---|---|
| S1 | Relevance | Feature keywords appear in ≥1 requirement title | Keywords in body but not titles | No keyword match to feature description |
| S2 | Specificity | No banned vague words in requirement titles | Vague words in descriptions only | Vague words in titles or acceptance criteria |
| S3 | Criteria | Every R{n} has Given/When/Then | ≥80% have criteria | <80% have criteria |
| S4 | RICE | All R{n} have RICE scores | Scores present but missing a dimension | No RICE scores |
| S5 | Scope | Now-tier has ≤10 requirements | 11-15 requirements | >15 (scope creep) |

**Banned vague words** (in titles/criteria): fast, intuitive, secure, scalable, robust, user-friendly, efficient, seamless, elegant, modern — unless followed by a measurable target (e.g., "fast: <200ms p95").

**Auto-fix:** Replace vague words with "[NEEDS METRIC]" and send back to PM once.

---

## DESIGN Eval

Run after Designer writes DESIGN.md. Skip in lite mode.

| # | Check | Pass | Warn | Fail |
|---|---|---|---|---|
| D1 | R→D coverage | Every frontend R{n} has ≥1 D-R{n} | 1 requirement missing | ≥2 requirements missing |
| D2 | Token usage | All specs use token references | 1-2 raw values found | >2 raw hex/px values in specs |
| D3 | States | Components have ≥5 states specified | ≥3 states per component | <3 states |
| D4 | Accessibility | Contrast ratios + keyboard specs present | One section missing | Both missing |
| D5 | Orphans | No D-R{n} without matching R{n} | — | Orphan D-R{n} found |

**Auto-fix:** Send gaps back to Designer with specific missing items.

---

## PLAN Eval

Run after Planner writes PLAN.md.

| # | Check | Pass | Warn | Fail |
|---|---|---|---|---|
| P1 | R→Phase coverage | Every R{n} in ≥1 phase | 1 requirement unmapped | ≥2 unmapped |
| P2 | Test gates | Every phase has a test gate | 1 phase missing gate | ≥2 missing |
| P3 | Task count | All phases have 1-8 tasks | 1 phase has 9-12 tasks | Any phase >12 tasks |
| P4 | Dependencies | Phase order makes sense (data→logic→UI) | — | UI phase before data phase with no justification |

**Auto-fix:** Send back to Planner with specific gaps.

---

## TECHNICAL Eval

Run after Architect writes TECHNICAL.md. Skip in lite mode.

| # | Check | Pass | Warn | Fail |
|---|---|---|---|---|
| T1 | R→T coverage | Every backend R{n} has ≥1 T-R{n} | 1 requirement missing | ≥2 missing |
| T2 | API completeness | All endpoints have request + response schemas | 1 endpoint incomplete | ≥2 incomplete |
| T3 | Data models | All entities have fields + types + constraints | Missing constraints | Missing field types |
| T4 | Error codes | Follow taxonomy format from skill | Minor inconsistency | No error handling section |
| T5 | Route conflicts | No path conflicts with PRODUCT.md routes | — | Conflicting routes found |

**Auto-fix:** Send back to Architect with specific gaps.

---

## PHASE Eval

Run after each implementation phase.

| # | Check | Pass | Warn | Fail |
|---|---|---|---|---|
| I1 | Tests | All pass | — | Any test failing |
| I2 | Lint | Clean | Warnings only | Errors |
| I3 | Types | Clean | — | Type errors |
| I4 | Criteria spot-check | Sampled Given/When/Then has matching test | Test exists but incomplete | No test for sampled criterion |

**Auto-fix:** Fix code, re-run tests. For I4, write the missing test.
