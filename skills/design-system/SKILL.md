---
name: design-system
description: UI/UX design methodology — user flows, visual design, component specs, design tokens, accessibility, and responsive behavior
user-invocable: false
---

# UI/UX Design System Methodology

Every design artifact must be specific enough for a developer to implement without ambiguity. All elements trace to SPEC.md requirements using `D-R{n}`. This skill covers visual design only — APIs, data models, and system architecture are handled by technical-architecture.

## 1. User Journey Mapping

Map user flow for each user-facing requirement before designing components.

```
### R{n}: [Title]
**Entry point:** [page, notification, deep link]
**Happy path:**
1. [Screen/State] → User [action] → System [response] → [Next]
**Error paths:**
- [Condition] → System [error state] → User [recovery]
**Decision points:**
- [Choice point] → [Options] → [Outcomes]
```

- Every user-facing requirement needs a journey map
- Backend-only requirements: "Technical — handled by architect agent"

## 2. Visual Theme & Atmosphere

Define overall visual personality before individual components:

- **Mood** — One-line reference ("Clean like Linear", "Warm like Notion")
- **Color approach** — Light/dark support, accent strategy, neutral temperature
- **Typography** — Font family matching codebase (geometric, humanist, monospace-tinged)
- **Density** — Compact (data-heavy) / comfortable (general) / spacious (marketing)
- **Motion** — Subtle (<200ms) / expressive (200-400ms) / minimal (prefers-reduced-motion only)

If project has an established theme (Tailwind config, theme files, PRODUCT.md), document and extend it.

## 3. Design Priority Hierarchy

When principles conflict, higher rank wins:

1. **Accessibility** — WCAG AA. Keyboard navigable. 4.5:1 text, 3:1 large text/UI contrast.
2. **Usability** — Task efficiency. Minimize cognitive load. Clear feedback.
3. **Consistency** — Match existing system. Reuse components.
4. **Responsiveness** — Mobile-first. Touch targets ≥44×44px.
5. **Performance** — Minimize DOM. Lazy load. No layout shifts.
6. **Aesthetics** — Visual polish. Spacing/color/type harmony.

## 4. Existing Pattern Discovery

Before designing anything new, explore and document:

- **Component library** — Existing components in `src/components/`, `app/components/`, `lib/ui/`. List with paths.
- **Design tokens** — Theme files, CSS variables, Tailwind config. Exact paths and key values.
- **CSS approach** — Tailwind / CSS modules / styled-components / vanilla. Follow it.
- **Layout patterns** — Page structure, grids, container widths, nav patterns.
- **Animation/icon patterns** — Existing transitions, easing, icon library.

Goal: extend existing patterns, never reinvent.

## 5. 3-Tier Token Architecture

Every value in a component spec must reference a token, never a raw value.

- **Tier 1 (Primitives)** — Raw values: colors (`gray-50: #F9FAFB`), spacing (`space-4: 16px`), radii, shadows
- **Tier 2 (Semantic)** — Purpose-mapped: `color-primary: {blue-600}`, `color-error: {red-600}`, `spacing-component-gap: {space-3}`
- **Tier 3 (Component)** — Component-specific: `button-primary-bg: {color-primary}`, `card-padding: {spacing-page-x}`

When codebase tokens exist, USE THEM. Only define new tokens for genuinely new values.

## 6. Component Specification Format

For each new component, specify ALL:

- **Purpose** — One sentence: what it does, when to use it.
- **Props/Variants** — Every prop with type and default.
- **States** — Token-referenced visuals for: Default, Hover (transition timing), Active, Focused (visible ring), Disabled (opacity, no pointer), Loading (spinner/skeleton), Error (border/message), Empty, Overflow, Selected, Skeleton, Drag/Drop, Read-only.
- **Dimensions** — Width, height, padding, margin via tokens.
- **Typography** — Size, weight, line-height, color via tokens.
- **Micro-interactions** — Hover (150-300ms), enter/exit, feedback animations. Specify easing + duration.
- **Accessibility** — ARIA role, labels, keyboard behavior (Tab/Enter/Escape), focus trap, screen reader text.
- **Responsive** — Exact behavior per breakpoint with px values.

**Never:** "nice padding" → `padding: {space-4} (16px)`. "primary color" → `bg: {color-primary} (#2563EB)`. "make it responsive" → "full-width below 640px, 50% above 768px".

## 7. Page/Screen Layout Specs

Show how components compose on actual screens:

```
### Page: [Name]
**Route:** /path
**Layout:** [sidebar+main, full-width, centered column]
**Component placement:** [ASCII diagram with dimensions]
**Responsive:** Below 768px: sidebar → hamburger. Below 640px: stack vertical.
```

## 8. Accessibility Audit

For every design, verify and document:

- **Contrast ratios** — Every foreground/background pair with ratio and AA pass/fail
- **Reduced-motion** — `prefers-reduced-motion` fallback for every animation
- **Screen reader** — `aria-live` for toasts, `aria-describedby` for validation, `aria-busy` for loading
- **Keyboard flow** — Tab order per page, focus traps (modals/dropdowns), skip links

## 9. Do's and Don'ts

Feature-specific guardrails table:

| Do | Don't | Why |
|---|---|---|
| Reuse existing variants | Create new components | Consistency |
| Use semantic tokens | Hardcode hex values | Theme-ability |
| Specify all states | Leave to "developer discretion" | Missing states = bugs |
| Design mobile first | Bolt on mobile after | Progressive enhancement |
| Provide skeleton loading | Show blank screens | Perceived performance |

## 10. Traceability

Every element maps to SPEC.md via `D-R{n}`:
- Components: `D-R1: NotificationBell` → R1
- Pages: `D-R2: Dashboard Page` → R2
- Multiple: `D-R1a`, `D-R1b` for multiple elements per requirement
- Backend-only R{n}: "**Technical — handled by architect agent**"
- If a user-facing R{n} has no D-R{n}, the design is incomplete.

## 11. DESIGN.md Output Template

```markdown
# UI/UX Design: [Feature Name]
**Last revised:** [date] — [summary if revised]

## Existing Patterns Referenced
## Visual Theme
## User Journeys
## Design Tokens (new only)
## Components
### D-R{n}: [Component Name]
**Traces to:** R{n}
[Purpose / Props / States / Dimensions / Typography / Interactions / A11y / Responsive]
## Page Layouts
## Accessibility Audit
## Do's and Don'ts
## Traceability Matrix
| Requirement | Design Element(s) | Type |
|---|---|---|
```

## 12. Incremental Design Rules

When existing design system exists:
1. Read existing patterns FIRST
2. Reuse ALL existing tokens — new only for genuinely new values
3. Visual consistency — same radius, shadow, spacing
4. State: "NEW: ComponentName" vs "MODIFIED: Button adds `notification` variant"

## 13. Validation Checklist

- [ ] Every user-facing R{n} has ≥1 D-R{n}; backend-only noted as "architect agent"
- [ ] All color pairs meet WCAG AA (4.5:1 text, 3:1 large/UI)
- [ ] All interactive components have keyboard + ARIA specs
- [ ] All animations have `prefers-reduced-motion` fallbacks
- [ ] All states specified (default, hover, active, focused, disabled, loading, error, empty)
- [ ] Token references everywhere — no raw hex/px/font values
- [ ] Existing patterns referenced by file path
- [ ] Responsive behavior with exact breakpoints
- [ ] Page layouts show composition, not just individual components
- [ ] Touch targets ≥44×44px on mobile
