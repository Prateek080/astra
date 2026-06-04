# Design Specs: {{FEATURE_NAME}}

**Generated:** {{TIMESTAMP}}
**Spec:** REQUIREMENTS.md
**Pipeline ID:** {{PIPELINE_ID}}

---

## Design System Context

### Existing Tokens
_Reference from graphify query or GRAPH_REPORT.md._

### Existing Components
_Reference from graphify query or GRAPH_REPORT.md._

---

## Component Specifications

### D-R1: {{COMPONENT_NAME}}
- **Requirement:** R1 — {{REQUIREMENT_TITLE}}
- **Status:** pending

#### User Flow
1. {{STEP_1}}
2. {{STEP_2}}

#### Layout
- **Container:** {{WIDTH}} x {{HEIGHT}}
- **Spacing:** {{SPACING_TOKEN}}
- **Breakpoints:** mobile (< 768px), tablet (768-1024px), desktop (> 1024px)

#### Visual Design
- **Background:** `--color-surface` / {{TOKEN}}
- **Text:** `--color-text-primary` / {{TOKEN}}
- **Border:** `--border-default` / {{TOKEN}}
- **Shadow:** `--shadow-sm` / {{TOKEN}}

#### States
| State | Visual Change | Trigger |
|-------|--------------|---------|
| Default | — | Initial render |
| Hover | {{CHANGE}} | Mouse enter |
| Active | {{CHANGE}} | Mouse down |
| Focused | {{CHANGE}} | Tab / click |
| Disabled | opacity: 0.5, cursor: not-allowed | `disabled` prop |
| Loading | Skeleton / spinner | Data fetching |
| Error | Error message, red border | Validation fail |
| Empty | Empty state illustration + CTA | No data |

#### Accessibility
- **Contrast:** 4.5:1 minimum (WCAG AA)
- **Keyboard:** Full tab navigation, Enter/Space to activate
- **ARIA:** `role="{{ROLE}}"`, `aria-label="{{LABEL}}"`
- **Touch target:** 44x44px minimum

---

## Traceability Matrix

| Requirement | Design Spec | Status |
|------------|-------------|--------|
| R1 | D-R1 | pending |

### Backend-only Requirements
_Requirements handled by architect agent (no UI component needed):_
- _None yet._

---

## Notes

- Every frontend R{n} must have >= 1 D-R{n}.
- Backend-only requirements: note as "Technical — handled by architect agent."
- Use design tokens, not raw hex/px values.
- Each component needs >= 5 states specified.
