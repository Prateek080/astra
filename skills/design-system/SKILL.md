---
name: design-system
description: UI/UX design methodology — user flows, visual design, component specs, design tokens, accessibility, and responsive behavior
user-invocable: false
---

# UI/UX Design System Methodology

This skill provides the methodology for the Designer agent. Every design artifact must be specific enough for a developer to implement without ambiguity. All elements trace back to SPEC.md requirements using the `D-R{n}` prefix. This skill covers visual design only — APIs, data models, and system architecture are handled by the technical-architecture skill.

---

## 1. User Journey Mapping

Before designing any components, map the user flow for each user-facing requirement in SPEC.md.

**Format per requirement:**

```
### R{n}: [Requirement Title]
**Entry point:** [Where the user starts — page, notification, deep link]
**Happy path:**
1. [Screen/State] → User [action] → System [response] → [Next screen/state]
2. ...
**Error paths:**
- [Condition] → System [shows error state] → User [recovery action]
**Decision points:**
- [Where user makes a choice] → [Options available] → [Outcomes]
```

**Rules:**
- Every user-facing requirement must have a journey map
- Identify entry point, happy path, error paths, and decision points
- This grounds component design in actual user behavior — don't design components in isolation
- Backend-only requirements get noted as "Technical — handled by architect agent"

---

## 2. Visual Theme & Atmosphere

Define the overall visual personality before designing individual components.

- **Mood** — One-line reference to a known product aesthetic (e.g., "Clean and focused like Linear" or "Warm and approachable like Notion"). This anchors all visual decisions.
- **Color approach** — Light/dark mode support? Primary accent strategy. Neutral palette temperature (cool grays vs warm grays).
- **Typography personality** — Modern geometric (Inter, Geist), humanist (Source Sans), monospace-tinged (JetBrains Mono). Must match or extend what exists in the codebase.
- **Density** — Compact (data-heavy apps), comfortable (general apps), spacious (marketing/creative). Drives spacing scale choices.
- **Motion personality** — Subtle (< 200ms, opacity/scale only), expressive (200-400ms, spring easing), minimal (prefers-reduced-motion only). Default to subtle unless the product demands expression.

If the project already has an established visual theme (found in theme files, Tailwind config, or PRODUCT.md), document it and ensure new designs are consistent.

---

## 3. Design Priority Hierarchy

When two principles conflict, the higher-ranked one wins.

1. **Accessibility** — WCAG AA minimum. Keyboard navigable. Screen reader compatible. 4.5:1 text contrast, 3:1 large text/UI.
2. **Usability** — Task completion efficiency. Minimize cognitive load. Prevent errors. Clear feedback for every action.
3. **Consistency** — Match existing design system. Reuse established components. No visual surprises.
4. **Responsiveness** — Mobile-first. All breakpoints. Touch targets at least 44x44px on mobile.
5. **Performance** — Minimize DOM nodes. Lazy load below-the-fold. Avoid layout shifts.
6. **Aesthetics** — Visual polish. Spacing harmony. Color balance. Typography rhythm.

---

## 4. Existing Pattern Discovery

Before designing anything new, explore the codebase. This is mandatory.

**Search for and document:**

- **Component library** — What UI components exist? Check `src/components/`, `app/components/`, `lib/ui/`, similar directories. List them with file paths.
- **Design tokens** — Theme files, CSS variables, Tailwind config, color definitions. Reference exact file paths and key values.
- **CSS approach** — Tailwind, CSS modules, styled-components, vanilla CSS? Whatever the project uses, follow it.
- **Layout patterns** — Page structure, grid systems, container widths, page padding, navigation patterns.
- **Animation patterns** — Existing transitions, easing functions, duration conventions.
- **Icon system** — Icon library (Lucide, Heroicons, custom SVGs), size conventions.

The goal: extend existing patterns, never reinvent. If the codebase uses Tailwind with `space-4` for component gaps, use `space-4`.

---

## 5. 3-Tier Token Architecture

Token examples are illustrative. The designer must discover and use the project's actual token system. If none exists, propose one consistent with the project's CSS approach.

Every value in a component spec must reference a token, never a raw value.

**Tier 1 — Primitive tokens** (raw values, the base palette):
- Colors: `gray-50: #F9FAFB`, `gray-900: #111827`, `blue-600: #2563EB`
- Spacing: `space-1: 4px`, `space-2: 8px`, `space-3: 12px`, `space-4: 16px`, `space-6: 24px`, `space-8: 32px`
- Radii: `radius-sm: 4px`, `radius-md: 8px`, `radius-lg: 12px`, `radius-full: 9999px`
- Shadows: `shadow-sm: 0 1px 2px rgba(0,0,0,0.05)`, `shadow-md: 0 4px 6px rgba(0,0,0,0.1)`

**Tier 2 — Semantic tokens** (purpose-mapped, reference primitives):
- `color-primary: {blue-600}`, `color-error: {red-600}`, `color-muted: {gray-500}`
- `color-surface: {white}`, `color-border: {gray-200}`, `color-text: {gray-900}`
- `spacing-page-x: {space-6}`, `spacing-component-gap: {space-3}`

**Tier 3 — Component tokens** (component-specific, reference semantic):
- `button-primary-bg: {color-primary}`, `button-primary-text: {white}`
- `card-padding: {spacing-page-x}`, `card-radius: {radius-card}`

When existing tokens are found in the codebase, USE THEM. Only define new tokens for genuinely new values.

---

## 6. Component Specification Format

For each new component, specify ALL of the following:

- **Purpose** — What it does and when to use it (one sentence).
- **Props/Variants** — Configurations: size (sm, md, lg), color variants, boolean flags. List every prop with type and default.
- **States** — Visual description for each state with token-referenced changes:
  - Default, Hover (transition timing), Active/Pressed, Focused (visible focus ring), Disabled (reduced opacity, no pointer events), Loading (spinner or skeleton), Error (error border/message), Empty (no data placeholder), Overflow (content exceeds bounds), Selected (active selection indicator), Skeleton (initial loading placeholder), Drag/Drop (if applicable), Read-only (view-only variant)
- **Dimensions** — Width, height, padding, margin using token references.
- **Typography** — Font size, weight, line-height, color using token references.
- **Micro-interactions** — Hover transitions (150-300ms), enter/exit animations, feedback animations (success checkmark, error shake). Specify easing and duration.
- **Accessibility** — ARIA role, `aria-label`/`aria-describedby`, keyboard behavior (Tab, Enter/Space, Escape), screen reader announcement text for dynamic content, focus trap (for modals/dropdowns).
- **Responsive** — Exact behavior per breakpoint with px values.

**Anti-patterns — never do these:**
- "nice padding" → say `padding: {space-4} (16px)`
- "primary color" → say `bg: {color-primary} (#2563EB)`
- "make it responsive" → say "full-width below 640px, 50% above 768px"
- "similar to the card" → say "uses `card-padding`, `card-radius` tokens; same shadow as `src/components/Card.tsx`"

---

## 7. Page/Screen Layout Specs

Don't just design components in isolation — show how they compose on actual screens.

**Per page/screen:**

```
### Page: [Page Name]
**Route:** /path/to/page
**Layout:** [grid type — sidebar+main, full-width, centered column]

**Component placement:**
┌─────────────────────────────────┐
│ Header (sticky, h: 64px)        │
├──────────┬──────────────────────┤
│ Sidebar  │ Main Content         │
│ (w: 256) │ (flex: 1)            │
│          │ ┌──────────────────┐ │
│          │ │ Component A      │ │
│          │ ├──────────────────┤ │
│          │ │ Component B      │ │
│          │ └──────────────────┘ │
├──────────┴──────────────────────┤
│ Footer (optional)               │
└─────────────────────────────────┘

**Responsive changes:**
- Below 768px: sidebar collapses to hamburger menu
- Below 640px: stack components vertically, full-width
```

This section bridges individual component specs and the actual user experience.

---

## 8. Accessibility Audit

For every design, verify and document:

**Contrast ratios** — List every foreground/background color pair with its ratio:

| Pair | Foreground | Background | Ratio | Pass |
|---|---|---|---|---|
| Body text | {color-text} #111827 | {color-surface} #FFFFFF | 15.4:1 | AA |
| Muted text | {color-muted} #6B7280 | {color-surface} #FFFFFF | 4.6:1 | AA |
| Button text | #FFFFFF | {color-primary} #2563EB | 4.7:1 | AA |

**Reduced-motion alternatives** — For every animation, specify a `prefers-reduced-motion` fallback:
- Fade transition (200ms) → instant opacity change
- Slide-in panel (300ms) → instant appear
- Loading spinner → static "Loading..." text

**Screen reader announcements** — For dynamic content changes:
- Toast notifications: `aria-live="polite"` with full message text
- Form validation: `aria-describedby` linking to error message
- Loading states: `aria-busy="true"` with `aria-label="Loading [context]"`

**Keyboard navigation flow** — Document the tab order for each page/screen. Note focus traps (modals, dropdowns) and skip links.

---

## 9. Do's and Don'ts

Feature-specific design guardrails. Customize these per feature based on what you learn during exploration.

**Format:**

| Do | Don't | Why |
|---|---|---|
| Reuse existing Button variants | Create a new button component | Consistency + maintenance |
| Use semantic color tokens | Hardcode hex values in components | Theme-ability, dark mode |
| Specify all component states | Leave states to "developer discretion" | Missing states = bugs |
| Design mobile layout first | Bolt on mobile as an afterthought | Better progressive enhancement |
| Provide skeleton loading states | Show blank screens while loading | Perceived performance |

---

## 10. Traceability

EVERY design element must map back to a SPEC.md requirement using `D-R{n}` identifiers:

- Components: `D-R1: NotificationBell` traces to R1
- Page layouts: `D-R2: Dashboard Page` traces to R2
- User journeys: `D-R3: Onboarding Flow` traces to R3
- Multiple elements per requirement: `D-R1a: NotificationBell`, `D-R1b: NotificationPanel`

A single element CAN map to multiple requirements, and a single requirement CAN have multiple elements.

If a requirement is backend-only (APIs, data models), note it as: "**Technical — handled by architect agent**" in the traceability matrix.

If a SPEC.md requirement has no corresponding design element AND is not backend-only, the design is incomplete.

---

## 11. DESIGN.md Output Template

Write the final design to `DESIGN.md` in the project root:

```markdown
# UI/UX Design: [Feature Name]

**Last revised:** [date] — [one-line summary if revised]

## Existing Patterns Referenced
- Component library: [path, key components found]
- Design tokens: [path, token system in use]
- CSS approach: [Tailwind / CSS modules / etc.]
- Layout patterns: [grid system, container widths]

## Visual Theme
- Mood: [reference product]
- Color approach: [light/dark, accent strategy]
- Typography: [font family, personality]
- Density: [compact/comfortable/spacious]
- Motion: [subtle/expressive/minimal]

## User Journeys
### R{n}: [Requirement Title]
Entry point → Happy path → Error paths → Decision points

## Design Tokens
### New Tokens (only if not already in codebase)
Tier 1 / Tier 2 / Tier 3 tables

## Components
### D-R{n}: [Component Name]
**Traces to:** R{n}
Purpose / Props / States / Dimensions / Typography /
Micro-interactions / Accessibility / Responsive

## Page Layouts
### Page: [Page Name]
Route / Layout / Component placement / Responsive changes

## Accessibility Audit
Contrast ratios / Reduced-motion / Screen reader / Keyboard navigation

## Do's and Don'ts
Feature-specific guardrails table

## Traceability Matrix
| Requirement | Design Element(s) | Type |
|---|---|---|
| R1 | D-R1: ComponentName | Component |
| R2 | Technical — architect agent | — |
```

---

## 12. Incremental Design Rules

When PRODUCT.md or an existing design system exists:

1. **Read existing patterns FIRST** — before proposing anything new.
2. **Reuse ALL existing tokens** — only define new tokens for genuinely new values.
3. **Visual consistency** — new components must look like they belong with existing ones. Same radius, shadow, spacing scale.
4. **Explicit extension vs modification** — state: "NEW: NotificationBell" vs "MODIFIED: Button now supports `notification` variant."
5. **Show diffs for modifications** — describe what changes and what stays the same.

---

## 13. Validation Checklist

Before finalizing the design, verify every item:

- [ ] Every user-facing R{n} has at least one D-R{n} design element
- [ ] Backend-only R{n} noted as "Technical — handled by architect agent"
- [ ] Traceability Matrix is complete — no requirement left unmapped
- [ ] All color pairs have contrast ratios meeting WCAG AA (4.5:1 text, 3:1 large/UI)
- [ ] All interactive components have keyboard behavior specified
- [ ] All components have ARIA roles or labels specified
- [ ] All animations have `prefers-reduced-motion` fallbacks
- [ ] All component states specified (default, hover, active, focused, disabled, loading, error, empty)
- [ ] Token references used everywhere — no raw hex, px, or font values in specs
- [ ] Existing codebase patterns referenced by file path, not reinvented
- [ ] Responsive behavior specified with exact breakpoints
- [ ] Page layouts show component composition, not just individual components
- [ ] User journeys map entry points, happy paths, and error paths
- [ ] Micro-interactions specify easing and duration
- [ ] Touch targets at least 44x44px on mobile
