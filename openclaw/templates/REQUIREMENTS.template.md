# Requirements: {{FEATURE_NAME}}

**Generated:** {{TIMESTAMP}}
**Mode:** {{MODE}}
**Pipeline ID:** {{PIPELINE_ID}}

---

## Summary

{{FEATURE_DESCRIPTION}}

---

## Requirements

### R1: {{REQUIREMENT_TITLE}}
- **Status:** pending
- **Priority:** P1 | Now
- **RICE:** Reach: {{R}} | Impact: {{I}} | Confidence: {{C}} | Effort: {{E}} | Score: {{SCORE}}
- **Assigned to:** —
- **Design:** pending
- **Technical:** pending

#### Acceptance Criteria

- **Given** {{PRECONDITION}}
- **When** {{ACTION}}
- **Then** {{EXPECTED_OUTCOME}}

---

## Priority Tiers

### Now (P1)
- R1: {{REQUIREMENT_TITLE}}

### Next (P2)
_None yet._

### Later (P3)
_None yet._

---

## Notes

- Requirements use stable IDs (R1, R2...) — never renumbered after creation.
- Status values: `pending` → `designed` → `specced` → `in_progress` → `implemented` → `verified`
- Each R{n} must have Given/When/Then acceptance criteria.
- No vague language — use concrete metrics ("fast" → "<200ms p95").
