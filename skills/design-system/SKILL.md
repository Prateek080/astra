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

Define overall visual personality before individual components. This is the most important step — every subsequent design decision must reference this direction.

### Mood Board

- **Mood** — One-line reference that captures the feeling ("Clean like Linear", "Warm like Notion", "Bold like Stripe", "Playful like Duolingo")
- **Personality** — 3-5 adjectives that define the product's character (e.g., "confident, calm, precise, friendly, modern")
- **Visual inspiration** — Name 2-3 products or brands whose design quality you're aiming for, and what specifically to learn from them

### Design Direction Decisions

These are not suggestions. They are decisions that the implementer must follow:

- **Color approach** — Light/dark support, accent strategy, neutral temperature. Specify: primary palette (3-5 colors), accent color, semantic colors (success/warning/error), neutral scale. NOT "use blue." Instead: "Primary: #2563EB (electric blue), accent: #7C3AED (violet), neutrals: warm gray scale from #F9FAFB to #111827."
- **Typography** — Font family matching codebase (geometric, humanist, monospace-tinged). Specify: heading font, body font, mono font, size scale (not just "use the default" — define the actual scale: h1=36px, h2=28px, etc.), weight usage (where to use bold, semibold, regular, light).
- **Density** — Compact (data-heavy) / comfortable (general) / spacious (marketing). Define: padding scale, gap scale, max content width.
- **Motion** — Subtle (<200ms) / expressive (200-400ms) / minimal (prefers-reduced-motion only). Define: default transition timing, easing curve, which elements animate.
- **Border radius philosophy** — Sharp (0-2px) / soft (4-8px) / rounded (12-16px) / pill (9999px). Be consistent.
- **Shadow philosophy** — None / subtle / layered. Define the shadow scale.
- **Icon style** — Outline / filled / duotone. Icon set name if applicable.

### The "Not Like This" Section

List 3-5 visual directions that this product should specifically AVOID:
- E.g., "Not corporate-blue-and-gray — this is not an enterprise dashboard"
- E.g., "Not playful-cartoon — this is a professional tool"
- E.g., "Not minimal-to-the-point-of-confusion — clarity beats aesthetics"

If project has an established theme (Tailwind config, theme files, PRODUCT.md), document and extend it. Never overwrite existing theme decisions — build on them.

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

## 13. Visual Quality Checklist

Beyond correctness (accessibility, states, tokens), every design must pass this quality gate. If any item fails, the design is not ready for implementation.

### Visual Hierarchy
- [ ] Eye path is clear — user knows where to look first, second, third without reading
- [ ] Primary action is visually dominant (color, size, position)
- [ ] Secondary actions are present but don't compete with primary
- [ ] Information density feels right — not cramped, not sparse, intentional

### Spacing & Layout
- [ ] Whitespace is generous — content breathes, doesn't suffocate
- [ ] Spacing follows a scale (4px base: 4, 8, 12, 16, 24, 32, 48, 64) — no arbitrary values
- [ ] Vertical rhythm is consistent — headings, paragraphs, sections follow spacing rules
- [ ] Container widths are defined — content doesn't stretch to infinity

### Typography
- [ ] Heading hierarchy is visually distinct — h1 vs h2 vs h3 is obvious at a glance
- [ ] Body text is readable — 16px minimum, 1.5-1.75 line height
- [ ] Font choices match product personality (defined in Section 2)
- [ ] No more than 2 font families (3 if mono is needed for code)

### Color
- [ ] Color palette is intentional and cohesive — not "default Tailwind blue"
- [ ] Accent color draws attention to interactive elements and key data
- [ ] Neutral scale has warmth/coolness matching the mood direction
- [ ] Every color has a purpose — no decorative color that doesn't serve UX

### Interaction Design
- [ ] Hover states are defined for every interactive element
- [ ] Active/pressed states give tactile feedback
- [ ] Loading states prevent layout shift (skeleton screens, not spinners on empty space)
- [ ] Error states are helpful (tell what's wrong, how to fix it)
- [ ] Empty states are designed (illustration or helpful message, not blank)
- [ ] Success feedback exists (toast, animation, state change)

### Micro-interactions
- [ ] Transitions have purpose — they guide attention, not decorate
- [ ] Timing feels natural — 150-300ms for hover, 200-400ms for enter/exit
- [ ] Easing curves are defined — ease-out for entering, ease-in for exiting
- [ ] No interaction feels broken or missing (every click/hover/tap has feedback)

### Overall Quality
- [ ] Design would not look out of place in a showcase of top product companies
- [ ] Design has personality — it's not generic, it's distinctly THIS product
- [ ] No "it works but it's boring" elements — every section has been designed, not just laid out
- [ ] Mobile experience is a first-class design, not a squeezed desktop layout

## 14. Design Review Gate

Before implementation begins, the reviewer agent must verify:

1. Section 2 (Visual Theme) is complete with all decisions filled in
2. Section 13 (Visual Quality Checklist) passes with zero unchecked items
3. Every component spec includes micro-interaction details, not just states
4. The "Not Like This" section exists and is specific
5. Typography scale, color palette, and spacing scale are explicitly defined with values

If any of these fail, send back to designer for revision before implementer starts.

## 15. Post-Implementation Visual Review

After implementer builds the UI, the designer must review the actual output:

1. Does the built UI match the design direction from Section 2?
2. Are the actual spacing values consistent with the defined scale?
3. Are transitions and micro-interactions implemented as specified?
4. Does the visual hierarchy work in practice, not just on paper?
5. Are there any "looks generic" moments that need visual improvement?
6. Does it feel like THIS product, or could it be anyone's product?

This review happens BEFORE the code reviewer checks functionality. Visual quality gates must pass before functional review.

## 16. Validation Checklist

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
- [ ] Visual Theme section (Section 2) is complete with all decisions
- [ ] Visual Quality Checklist (Section 13) passes
- [ ] "Not Like This" section exists with specific anti-patterns
- [ ] Typography scale, color palette, spacing scale defined with explicit values
- [ ] Micro-interactions specified for every interactive component
