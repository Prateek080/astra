---
name: design-system
description: Design methodology for producing implementable UI specs, system architecture, and API designs with full requirement traceability
user-invocable: false
---

# Design System Methodology

This skill provides the methodology for the Designer agent. Every design artifact produced must be specific enough for a developer to implement without ambiguity, and every element must trace back to a SPEC.md requirement.

---

## 1. Feature Type Detection

Before designing, classify the feature by scanning SPEC.md requirements:

| Classification | Condition | Output Sections |
|---|---|---|
| **Frontend** | All requirements involve UI, components, pages, interactions | Visual Theme, Colors, Typography, Components, Layout, Responsive |
| **Backend** | All requirements involve APIs, data, services, infrastructure | API Design, Data Model, System Architecture, Error Handling |
| **Full-stack** | Mix of both | All sections |

Detection rules: If every requirement relates to user-facing elements, it is frontend. If every requirement relates to data or services, it is backend. Any mix is full-stack. This classification determines which sections of DESIGN.md to produce.

If unclear, default to full-stack. Ask the calling agent to clarify if the spec genuinely has no indicators.

---

## 2. Design Priority Hierarchy

Every design decision must follow this priority order. When two principles conflict, the higher-ranked one wins.

1. **Accessibility** — WCAG AA minimum. All interactive elements keyboard navigable. Screen reader compatible. Sufficient color contrast (4.5:1 text, 3:1 large text/UI components).
2. **Usability** — Task completion efficiency. Minimize cognitive load. Prevent errors before they happen. Provide clear feedback for every action.
3. **Consistency** — Match the existing design system. Reuse established components and patterns. No visual surprises.
4. **Responsiveness** — Mobile-first approach. Works across all breakpoints. Touch targets at least 44x44px on mobile.
5. **Performance** — Minimize DOM nodes. Lazy load below-the-fold content. Optimize images. Avoid layout shifts.
6. **Aesthetics** — Visual polish. Spacing harmony. Color balance. Typography rhythm.

---

## 3. Existing Pattern Discovery

Before designing anything new, explore the codebase for existing patterns. This is mandatory, not optional.

**Search for and document:**

- **Component library** — What UI components already exist? Check `src/components/`, `app/components/`, `lib/ui/`, and similar directories. List them.
- **Design tokens** — Theme files, CSS variables, Tailwind config, color definitions. Reference exact file paths.
- **CSS approach** — Tailwind, CSS modules, styled-components, vanilla CSS? Whatever the project uses, follow it.
- **Layout patterns** — How are existing pages structured? Grid, Flex, container widths, page padding.
- **API patterns** — REST or GraphQL? Response envelope format? Authentication mechanism? Error response shape.
- **Data layer** — ORM (Prisma, Drizzle, SQLAlchemy)? Database type? Migration tool?
- **Error patterns** — How are errors displayed to users? Toast, inline, page-level? How are API errors structured?

The goal: extend existing patterns, never reinvent them. If the codebase uses Tailwind with `space-4` for component gaps, the design must reference `space-4`, not invent a new spacing value.

---

## 4. Frontend Design Methodology

### 3-Tier Token Architecture

Token examples below are illustrative. The designer must discover and use the project's actual token system. If none exists, propose one consistent with the project's CSS/styling approach.

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
- `radius-card: {radius-lg}`, `radius-button: {radius-md}`, `radius-input: {radius-md}`

**Tier 3 — Component tokens** (component-specific, reference semantic tokens):
- `button-primary-bg: {color-primary}`, `button-primary-text: {white}`
- `card-padding: {spacing-page-x}`, `card-radius: {radius-card}`
- `input-border: {color-border}`, `input-focus-ring: {color-primary}`

When existing design tokens are found in the codebase, USE THEM. Only define new tokens for genuinely new values.

### Component Specification Format

For each new component, specify ALL of the following:

- **Purpose** — What it does and when to use it (one sentence).
- **Props/Variants** — Configurations it accepts: size (sm, md, lg), color variants, boolean flags. List every prop with its type and default.
- **States** — Visual description for each state, with exact token-referenced changes:
  - Default, Hover, Active/Pressed, Focused (visible focus ring), Disabled (reduced opacity, no pointer events), Loading (spinner or skeleton), Error (error border/message), Empty (no data/content placeholder), Overflow (content exceeds bounds), Selected (active selection indicator)
- **Dimensions** — Width, height, padding, margin using token references. Example: `padding: {space-3} {space-4}` (12px 16px).
- **Typography** — Font size, weight, line-height, color using token references.
- **Accessibility** — ARIA role, `aria-label`/`aria-describedby`, keyboard behavior (Tab to focus, Enter/Space to activate, Escape to dismiss), screen reader announcements.
- **Responsive** — Exact behavior per breakpoint. Example: "full-width below 640px, 50% width above 768px, fixed 320px above 1024px."

**Anti-patterns — never do these:**
- "nice padding" — say `padding: {space-4} (16px)`
- "primary color" — say `bg: {color-primary} (#2563EB)`
- "make it responsive" — say "full-width below 640px, 50% above 768px"
- "similar to the card component" — say "uses `card-padding`, `card-radius` tokens; same shadow as existing Card component in `src/components/Card.tsx`"

---

## 5. Backend Design Methodology

### API Design

For each endpoint, specify:

- **Method + Path** — Following existing REST conventions found in the codebase.
- **Request schema** — JSON with types, required/optional markers, validation rules (min/max length, regex patterns, enum values).
- **Response schema** — JSON matching the existing envelope format. Include both success and error shapes.
- **Status codes** — Only those that apply: 200 (success), 201 (created), 400 (validation), 401 (unauthenticated), 403 (unauthorized), 404 (not found), 422 (unprocessable), 409 (conflict), 500 (server error).
- **Auth** — Public, authenticated, or specific role required.
- **Rate limiting** — If applicable, requests per window.

### Data Model

For each entity, specify:

- **Fields** — Name, type, constraints (NOT NULL, UNIQUE, DEFAULT, CHECK), and purpose.
- **Relationships** — belongs-to, has-many, many-to-many with explicit foreign key names and cascade behavior.
- **Indexes** — Which fields, index type (btree, unique, composite), and the query pattern that justifies each index.
- **Migrations** — New table, add column, modify constraint. State whether this is additive or breaking.

### System Architecture

For complex flows, write a numbered sequence:

```
1. Client sends POST /api/orders with payload
2. Server validates request body against schema
3. Server checks user authorization
4. Database: INSERT into orders table within transaction
5. Database: UPDATE inventory (decrement stock) within same transaction
6. Event: OrderCreated emitted to queue
7. Response: 201 with created order object
```

Call out external dependencies explicitly. Document the error propagation path: where does each error type get caught and how does it surface to the client?

---

## 6. Traceability Requirement

EVERY design element must map back to a SPEC.md requirement using `D-R{n}` identifiers:

- Components: `D-R1: NotificationBell` traces to R1
- API endpoints: `D-R3: POST /api/notifications` traces to R3
- Data models: `D-R2: notifications table` traces to R2
- Multiple elements per requirement: `D-R1a: NotificationBell`, `D-R1b: NotificationPanel`

A single design element CAN map to multiple requirements (e.g., `D-R1,R3: NotificationBell` for a component that satisfies both R1 and R3), and a single requirement CAN have multiple design elements (e.g., `D-R1a: NotificationBell`, `D-R1b: NotificationPanel`).

If a SPEC.md requirement has no corresponding design element, the design is incomplete. The Traceability Matrix must account for every R{n}.

---

## 7. DESIGN.md Output Template

The output must follow this structure. Include frontend sections for frontend/full-stack features, backend sections for backend/full-stack features.

```markdown
# Design: [Feature Name]

## Feature Type
[frontend / backend / full-stack]

## Existing Patterns Referenced
- Component library: [path, key components found]
- Design tokens: [path, token system in use]
- CSS approach: [Tailwind / CSS modules / etc.]
- API conventions: [REST pattern, envelope format]
- Data layer: [ORM, database type]

## Design Decisions
| Decision | Rationale | Traces to |
|---|---|---|
| [What was decided] | [Why] | [R-ids] |

<!-- FRONTEND SECTIONS (include for frontend / full-stack) -->

## Visual Theme
## Colors — table: Token | Value | Usage | Contrast Ratio
## Typography — table: Scale | Size | Weight | Line Height | Usage

## Components
### D-R{n}: [Component Name]
**Traces to:** R{n}
**Purpose / Props / States / Dimensions / Typography / Accessibility / Responsive**
(See Section 4 for required fields per component)

## Layout
## Responsive Behavior — table: Breakpoint | Layout Change

<!-- BACKEND SECTIONS (include for backend / full-stack) -->

## API Design
### D-R{n}: [Endpoint Name]
**Traces to:** R{n}
**Method / Path / Auth / Request schema / Response schema / Errors**
(See Section 5 for required fields per endpoint)

## Data Model
### D-R{n}: [Entity Name]
**Traces to:** R{n}
Field table + Relationships + Indexes
(See Section 5 for required fields per entity)

## System Architecture — numbered sequence flow
## Error Handling — table: Error Source | Error Type | Client Response

<!-- ALWAYS INCLUDE -->

## Traceability Matrix
| Requirement | Design Element(s) | Type |
|---|---|---|
| R1 | D-R1: ComponentName | Component |
| R2 | D-R2: EntityName | Data Model |
```

---

## 8. Incremental Design Rules

When PRODUCT.md or an existing design system exists:

1. **Read existing patterns FIRST** — before proposing anything new.
2. **Reuse ALL existing tokens** — only define new tokens for values that genuinely do not exist.
3. **Visual consistency** — new components must look like they belong with existing ones. Same border radius, same shadow depth, same spacing scale.
4. **API consistency** — new endpoints must use the same response envelope, error format, and naming conventions as existing ones.
5. **Data model consistency** — follow existing naming conventions (snake_case vs camelCase, singular vs plural table names, timestamp column names).
6. **Explicit extension vs modification** — state clearly: "NEW: NotificationBell component" vs "MODIFIED: Button now supports `notification` variant (new badge prop)."
7. **Show diffs for modifications** — when changing existing components or endpoints, describe what changes and what stays the same.

---

## 9. Validation Checklist

Before finalizing the design, verify every item:

- [ ] Every R{n} from SPEC.md has at least one D-R{n} design element
- [ ] Traceability Matrix is complete — no requirement left unmapped
- [ ] All color values have contrast ratios meeting WCAG AA (4.5:1 normal text, 3:1 large text and UI)
- [ ] All interactive components have keyboard behavior specified (Tab, Enter, Space, Escape)
- [ ] All components have ARIA roles or labels specified
- [ ] All API endpoints have complete request and response schemas
- [ ] All data model fields have types, constraints, and relationships defined
- [ ] Token references are used everywhere — no raw hex, px, or font values in component specs
- [ ] Existing codebase patterns are referenced by file path, not reinvented
- [ ] Responsive behavior is specified with exact breakpoints, not vague descriptions
- [ ] Feature type classification matches the output sections included
- [ ] Design decisions table includes rationale and requirement traces
