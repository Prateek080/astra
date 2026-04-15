# Research: PM Agent & UI/UX Designer Agent Skills

## Sources Fetched

| # | Source | Status | Content Quality |
|---|--------|--------|----------------|
| 1 | deanpeters/Product-Manager-Skills `skills/prd-development/SKILL.md` | Fetched | Excellent - full 8-phase workflow with orchestration |
| 2 | github/awesome-copilot `agents/prd.agent.md` | Fetched | Good - GitHub's official PRD agent with tools |
| 3 | KhazP/vibe-coding-prompt-template `README.md` | Fetched | Good - 5-stage workflow with file structure |
| 4 | nextlevelbuilder/ui-ux-pro-max-skill `.claude/skills/ui-ux-pro-max/SKILL.md` | Fetched | Excellent - 45KB skill with reasoning engine, 161 rules |
| 4b | nextlevelbuilder/ui-ux-pro-max-skill `.claude/skills/design-system/SKILL.md` | Fetched | Good - 3-layer token architecture |
| 5 | VoltAgent/awesome-design-md `design-md/linear.app/DESIGN.md` | Fetched | Excellent - complete DESIGN.md exemplar (Linear) |
| 6 | sdi2200262/agentic-project-management (Manager Agent + Task Assignment + Agent Types + Handover) | Fetched | Excellent - full multi-agent orchestration system |

---

## SECTION A: PM / PRD Agent

### A1. Key Structural Pattern (from Source 1: deanpeters)

**Eight-phase PRD workflow with sub-skill orchestration:**

```
Phase 1: Executive Summary (30 min)
  Template: "We're building [solution] for [persona] to solve [problem], resulting in [impact]."

Phase 2: Problem Statement (60 min)
  Sub-skill: problem-statement/SKILL.md
  Required: affected users, core problem, pain points, evidence (quotes, data)

Phase 3: Target Users & Personas (30 min)
  Sub-skill: proto-persona/SKILL.md
  Required: role, goals, pain points, behaviors

Phase 4: Strategic Context (45 min)
  Sub-skill: tam-sam-som-calculator/SKILL.md
  Required: business OKRs link, TAM/SAM/SOM, competitive landscape, timing

Phase 5: Solution Overview (60 min)
  Sub-skill: user-story-mapping-workshop/SKILL.md
  Required: 2-3 paragraph description, user flows, story map reference

Phase 6: Success Metrics (30 min)
  Required: primary metric (single optimization target), secondary, guardrail metrics

Phase 7: User Stories & Requirements (90-120 min)
  Sub-skills: epic-hypothesis, user-story, epic-breakdown-advisor
  Required: epic hypothesis, 3-10 user stories with acceptance criteria

Phase 8: Out of Scope & Dependencies (30 min)
  Required: excluded features with rationale, dependencies, risks, open questions
```

**Frontmatter pattern:**
```yaml
name: prd-development
description: Build a structured PRD connecting problem, users, solution, success criteria
intent: Guide through structured PRD creation by orchestrating problem framing, user research synthesis, solution definition, and success criteria
type: workflow
theme: pm-artifacts
best_for:
  - "Writing a complete PRD from scratch"
  - "Structuring product requirements for engineering handoff"
scenarios:
  - "I need a PRD for a new AI-powered recommendation feature"
estimated_time: "60-120 min"
```

**Anti-patterns explicitly called out:**
- Excessive specification (PRDs frame problems, don't mandate pixel-level design)
- Waterfall rigidity (documents evolve, not frozen contracts)
- Collaboration substitution (complement discussion, don't replace it)
- Problem ambiguity (missing customer evidence undermines credibility)
- Unchecked scope (undefined out-of-scope invites feature creep)

**Directly reusable:** The 8-phase structure, sub-skill orchestration model, template sentence, and anti-pattern list.

---

### A2. GitHub's Official PRD Agent (Source 2)

**Key differentiator: Tool-integrated approach**

```yaml
tools: ["codebase", "edit/editFiles", "fetch", "findTestFiles", "list_issues",
"githubRepo", "search", "add_issue_comment", "create_issue", "update_issue",
"get_issue", "search_issues"]
```

**Workflow: Pre-draft questioning -> Codebase analysis -> Document creation -> Issue creation**

Critical technique: **3-5 clarifying questions BEFORE drafting.** The agent gathers:
- Target audience
- Features and constraints
- Technical context from existing codebase

**Output spec:**
- Valid Markdown only, no disclaimers or horizontal rules
- User story IDs: unique identifiers (e.g., GH-001)
- File location: `prd.md` in user-specified or default location
- Conversational tone with precise metrics

**PRD sections:**
1. Product overview
2. Goals (business/user/non-goals)
3. User personas
4. Functional requirements
5. User experience flows
6. Narrative
7. Success metrics
8. Technical considerations
9. Milestones
10. User stories with acceptance criteria

**Directly reusable:** The tool integration pattern (codebase + issue tracker), the pre-draft questioning technique, and the non-goals section.

---

### A3. Vibe-Coding 5-Stage Template (Source 3)

**Key insight: Separate "thinking" from "building" phases**

```
Phase 1: Research & Definition (Chat-based, ~60 min)
  Step 1: Deep Research (20-30 min) - Validate demand and scope
  Step 2: Product Requirements (15-20 min) - Define MVP functionality
  Step 3: Technical Design (15-20 min) - Select technology stack

Phase 2: Execution (IDE-based)
  Step 4: Agent File Setup (1-2 min) - Populate AGENTS.md
  Step 5: Build with AI Agent (1-3 hrs) - Iterative development
```

**File structure pattern:**
```
your-app/
  docs/
  agent_docs/
  AGENTS.md          # Master instructions
  specs/
  .cursor/rules/
  src/
```

**Directly reusable:** The chat-first-then-IDE workflow, the AGENTS.md master file concept, and the separation of research/definition from execution.

---

### A4. Synthesized PM Agent Framework

Combining all three sources, the strongest PM agent would have:

1. **Pre-work phase** (from GitHub agent): 3-5 clarifying questions + codebase analysis
2. **Structured document phases** (from deanpeters): 8-phase workflow with sub-skill delegation
3. **Clear separation** (from vibe-coding): Research/definition before execution
4. **Tool integration** (from GitHub agent): Issue tracker + codebase search
5. **Anti-pattern guardrails** (from deanpeters): Explicit "what NOT to do"
6. **Output artifact** (all three): Standardized PRD markdown with consistent sections

---

## SECTION B: UI/UX Designer Agent

### B1. UI/UX Pro Max Reasoning Engine (Source 4)

**This is the most comprehensive design skill found (45KB). Key architecture:**

**Priority-ranked reasoning system (1-10):**

| Priority | Category | Severity |
|----------|----------|----------|
| 1 | Accessibility | CRITICAL |
| 2 | Touch/Interaction | CRITICAL |
| 3 | Performance | HIGH |
| 4 | Style Selection | HIGH |
| 5 | Layout & Responsive | HIGH |
| 6 | Typography | MEDIUM |
| 7 | Animation | MEDIUM |
| 8 | Forms | MEDIUM |
| 9 | Navigation | HIGH |
| 10 | Charts/Data Viz | LOW |

**Three-phase design system generation:**

```
Phase 1: Analysis
  - Extract product type, target audience, style keywords, tech stack

Phase 2: System Generation
  - Multi-domain search across 11 domains (product, style, color, typography,
    landing, chart, ux, google-fonts, stack, web, prompt)
  - Outputs: pattern + style + colors + typography + effects + anti-patterns + checklist

Phase 3: Hierarchical Persistence (Master + Page Overrides)
  - MASTER.md = global source of truth
  - design-system/pages/[name].md = context-specific overrides
  - Retrieval: page overrides > master defaults
```

**Pre-delivery validation (3-tier checklist):**

```
Tier 1 (CRITICAL): Accessibility + Touch
  - Contrast 4.5:1 verified
  - Touch targets >= 44x44pt
  - Focus states visible
  - Screen reader labels

Tier 2 (HIGH): Performance + Style + Layout
  - CLS < 0.1
  - Safe-area compliance
  - Responsive breakpoints tested
  - Style consistency

Tier 3 (QUALITY): Typography + Animation + Forms + Nav + Charts
  - Animation 150-300ms
  - Form error placement
  - Navigation deep-linking
  - Dark mode contrast parity
```

**Key anti-patterns encoded:**

| Rule | Anti-Pattern |
|------|-------------|
| Touch target >= 44x44pt | Tiny tap targets without expanded hit area |
| Semantic color tokens | Raw hex values hardcoded per-screen |
| Inline validation on blur | Validating on keystroke |
| Platform-native controls | Generic containers without semantics |
| Bottom nav <= 5 items | Overloaded navigation with 10+ items |
| Visible focus rings | Removing focus indicators |

**Directly reusable:** Priority hierarchy, 3-tier validation checklist, anti-pattern pairing, master+override persistence model, multi-domain search concept.

---

### B2. Design System Token Architecture (Source 4b)

**Three-layer token system:**

```
Layer 1 - Primitive:  --color-blue-600: #2563EB
Layer 2 - Semantic:   --color-primary: var(--color-blue-600)
Layer 3 - Component:  --button-bg: var(--color-primary)
```

**Validation rules:**
- All artifacts must import centralized `design-tokens.css`
- Use CSS variables exclusively: `var(--token-name)`
- No hardcoded values (hex, font names, measurements)
- Component specs must include: Default, Hover, Active, Disabled states

**Directly reusable:** The 3-layer token hierarchy and the state-matrix component spec pattern.

---

### B3. DESIGN.md Format (Source 5: VoltAgent/Linear example)

**9-section standard structure:**

```
1. Visual Theme & Atmosphere
   - Mood, density, design philosophy

2. Color Palette & Roles
   - Semantic names, hex values, functional roles
   - Example: background #08090a, text #f7f8f8, accent #5e6ad2

3. Typography Rules
   - Font families with OpenType features
   - 25+ text styles in hierarchy table
   - Signature weights and rendering notes

4. Component Stylings
   - Buttons, cards, inputs, badges, navigation
   - State specifications (default, hover, active, disabled)

5. Layout Principles
   - Spacing system, grid structure, whitespace philosophy
   - Border radius scale

6. Depth & Elevation
   - Shadow hierarchy and elevation levels

7. Do's and Don'ts
   - Implementation guardrails

8. Responsive Behavior
   - Breakpoints, touch targets, collapse strategies

9. Agent Prompt Guide
   - Color reference table
   - Ready-to-use component generation prompts
   - Iteration instructions
```

**Key insight from VoltAgent:** Section 9 "Agent Prompt Guide" is specifically designed for AI agents to consume the design system. It provides ready-to-use prompts like: "Generate a card component using the color palette and elevation system defined above."

**Directly reusable:** The entire 9-section structure as our DESIGN.md output format. The Agent Prompt Guide section is a novel pattern worth adopting.

---

### B4. Synthesized UI/UX Agent Framework

Combining sources 4, 4b, and 5:

1. **Reasoning engine** (from Pro Max): Priority 1-10 hierarchy for design decisions
2. **Design system generation** (from Pro Max): Analysis -> Generation -> Persistence
3. **Token architecture** (from design-system skill): 3-layer primitive/semantic/component
4. **Output format** (from DESIGN.md): 9-section standardized document
5. **Validation** (from Pro Max): 3-tier pre-delivery checklist
6. **Anti-patterns** (from Pro Max): Paired with every rule
7. **Master + Override model** (from Pro Max): Global design system with page-specific overrides

---

## SECTION C: Multi-Agent Orchestration (Source 6: APM)

### C1. Agent Type Architecture

**Four specialized agents by context scope (not persona):**

| Type | Function | Scope | Lifecycle |
|------|----------|-------|-----------|
| Setup Agent | Architect | Full project vision | Temporary (project start) |
| Manager Agent | Coordinator | Big picture planning | Entire project |
| Implementation Agent | Builder | Specific tasks | As assigned |
| Ad-Hoc Agent | Specialist | Isolated problems | Temporary (task-scoped) |

**Critical design principle:** Agents are scoped by context, not persona. Each receives ONLY information relevant to their specific role.

### C2. Manager Agent Protocol

**Core constraints:**
- EXPLICITLY PROHIBITED from executing implementation, coding, or research
- Can only: assign tasks, review logs, maintain plans, monitor context windows

**Session initialization (two paths):**
1. Post-setup: Read Implementation Plan -> validate -> integrate guides -> present summary -> initialize Memory Root
2. Handover: Request Handover Prompt -> cross-reference Plan vs logs -> identify contradictions -> present progress -> seek verification

**Decision framework:**
- Read Memory_Root.md to detect session type
- Validate plan structure before execution
- Request clarification when instructions lack clarity
- Proactively initiate handover approaching context limits

### C3. Task Assignment Protocol

**Task Loop:** prompt creation -> execution -> work logging -> review -> next action

**Dependency handling (two types):**
- Same-agent: "Simple Contextual Reference" with brief integration guidance
- Cross-agent: "Comprehensive Integration Context" requiring file reading + output summaries

**Next Action Framework (three pathways):**
1. Continue: issue next assignment
2. Follow-Up: send corrections
3. Update Plan: when assumptions prove invalid

### C4. Handover Protocol

**Triggers:** Approaching token/context limits after completing current task cycle.

**Two artifacts generated:**
1. Handover Prompt (chat-based): file references, log citations, phase status, agent assignments, priority tasks
2. Handover File (markdown): YAML metadata, unlogged directives, coordination dependencies, agent performance insights, blocked items

**Blocking scenarios:** No handover during task execution waits, log retrieval delays, or ongoing reviews.

### C5. Directly Reusable Orchestration Patterns

1. **Context-scoped agents** (not persona-scoped): Each agent gets only relevant context
2. **Manager-cannot-implement rule**: Strict separation of coordination from execution
3. **Memory Root + Memory Logs**: Persistent state across agent sessions
4. **Two-type dependency handling**: Same-agent (lightweight) vs cross-agent (comprehensive)
5. **Handover protocol**: Structured context transfer when approaching limits
6. **Implementation Plan as source of truth**: Single artifact that all agents reference
7. **Ad-hoc delegation for context-heavy work**: Temporary agents for debugging/research

---

## SECTION D: Recommendations for Our Implementation

### For PM Agent skill:

**Structure:** Adopt deanpeters' 8-phase workflow as the backbone, with GitHub agent's pre-draft questioning and tool integration.

**Key sections to include:**
1. Frontmatter with `type: workflow`, `intent`, `best_for`, `scenarios`
2. Pre-work: 3-5 clarifying questions + codebase analysis
3. Phased PRD creation (executive summary -> problem -> personas -> strategy -> solution -> metrics -> stories -> scope)
4. Each phase references sub-skills where applicable
5. Anti-pattern guardrails at each phase
6. Output: standardized PRD markdown with user story IDs
7. Post-creation: optional issue tracker integration

**Novel techniques to adopt:**
- Epic hypothesis statement format
- Guardrail metrics (protect against regression, not just measure success)
- TAM/SAM/SOM calculator integration
- "When to use / when to skip" guidance

### For UI/UX Designer Agent skill:

**Structure:** Adopt Pro Max's priority-ranked reasoning engine with VoltAgent's DESIGN.md output format.

**Key sections to include:**
1. Frontmatter with `type: interactive`, design-specific metadata
2. Priority 1-10 reasoning hierarchy for all design decisions
3. Three-phase workflow: Analysis -> System Generation -> Persistence
4. 3-layer token architecture (primitive -> semantic -> component)
5. 9-section DESIGN.md output format (from VoltAgent)
6. 3-tier pre-delivery validation checklist
7. Anti-pattern pairs for every rule
8. Master + page-override persistence model
9. Platform-specific idioms (iOS HIG, Material Design)

**Novel techniques to adopt:**
- Agent Prompt Guide section in DESIGN.md (section 9)
- State-matrix component specs (default/hover/active/disabled)
- Hierarchical persistence (MASTER.md + page overrides)
- Multi-domain search across product/style/color/typography/UX

### For Orchestration:

**Adopt from APM:**
- Context-scoped agent design (each agent gets only relevant info)
- Manager-cannot-implement separation
- Structured handover protocol with two artifacts
- Same-agent vs cross-agent dependency handling
- Implementation Plan as single source of truth
- Ad-hoc agent pattern for isolated, context-heavy tasks

---

## SECTION E: Raw Reference Material

### E1. PRD Section Template (Composite)

```markdown
# [Product Name] - Product Requirements Document

## Executive Summary
We're building [solution] for [persona] to solve [problem], resulting in [impact].

## Problem Statement
### Who is affected
### What is the core problem
### Why does it matter now
### Evidence (customer quotes, data, support tickets)

## Target Users & Personas
### Primary Persona
- Role:
- Goals:
- Pain points:
- Key behaviors:

### Secondary Persona(s)

## Goals
### Business Goals
### User Goals
### Non-Goals (explicitly excluded objectives)

## Strategic Context
### Business OKR alignment
### Market opportunity (TAM/SAM/SOM)
### Competitive positioning
### Timing rationale

## Solution Overview
[2-3 paragraph high-level description]
### Key user flows
### Core features

## Success Metrics
### Primary metric (single optimization target)
### Secondary metrics
### Guardrail metrics (protect against regression)

## User Stories & Requirements
### Epic Hypothesis
We believe that [capability] will result in [outcome]. We will know we are right when [metric] changes by [amount].

### User Stories
- **GH-001**: As a [persona], I want [action] so that [benefit]
  - Acceptance criteria:
    - [ ] Given [context], when [action], then [result]

## User Experience
### Key flows (narrative form)
### Wireframe/mockup references

## Technical Considerations
### Architecture constraints
### Integration points
### Performance requirements
### Security considerations

## Out of Scope
| Feature | Rationale for exclusion |
|---------|----------------------|

## Dependencies & Risks
### Technical dependencies
### External dependencies
### Risk register with mitigation strategies

## Milestones & Timeline
### Phase 1: ...
### Phase 2: ...

## Open Questions
- [ ] Question 1
- [ ] Question 2
```

### E2. DESIGN.md Section Template (from VoltAgent format)

```markdown
# [Product] Design System

## 1. Visual Theme & Atmosphere
- **Mood:**
- **Density:**
- **Design philosophy:**

## 2. Color Palette & Roles
| Token | Hex | Role |
|-------|-----|------|
| --color-bg-primary | | Main background |
| --color-bg-elevated | | Cards, modals |
| --color-text-primary | | Body text |
| --color-accent | | Interactive elements |
| --color-error | | Error states |
| --color-success | | Success states |

## 3. Typography Rules
- **Primary font:**
- **Secondary font:**
- **Monospace font:**

| Style | Size | Weight | Line Height | Use |
|-------|------|--------|-------------|-----|
| Display | | | | |
| Headline | | | | |
| Title | | | | |
| Body | | | | |
| Label | | | | |
| Caption | | | | |

## 4. Component Stylings
### Buttons
| Property | Default | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | | | | |
| Text | | | | |
| Border | | | | |
| Shadow | | | | |

### Cards
### Inputs
### Navigation

## 5. Layout Principles
- **Spacing scale:**
- **Grid:**
- **Max content width:**
- **Border radius scale:**

## 6. Depth & Elevation
| Level | Use | Shadow |
|-------|-----|--------|
| 0 | Flat surfaces | |
| 1 | Cards | |
| 2 | Dropdowns | |
| 3 | Modals | |

## 7. Do's and Don'ts
### Do
### Don't

## 8. Responsive Behavior
| Breakpoint | Width | Layout changes |
|------------|-------|---------------|

## 9. Agent Prompt Guide
### Color reference
### Component generation prompts
### Iteration guide
```

### E3. Multi-Agent Orchestration Template (from APM)

```
Agent Types:
  Setup Agent (Architect) -> temporary, creates Implementation Plan
  Manager Agent (Coordinator) -> persistent, assigns and reviews
  Implementation Agent (Builder) -> task-scoped, executes work
  Ad-Hoc Agent (Specialist) -> temporary, isolated context-heavy tasks

Workflow:
  1. Setup Phase: Setup Agent interviews user -> creates Implementation Plan
  2. Task Loop: Manager reads Plan -> assigns task -> Implementation executes -> logs Memory -> Manager reviews -> next action
  3. Handover: When approaching context limits -> generate Handover Prompt + Handover File -> new Manager resumes

Artifacts:
  - Implementation_Plan.md (source of truth)
  - Memory_Root.md (session state index)
  - Memory Logs (per-task output records)
  - Handover Files (context transfer documents)
  - Task Assignment Prompts (YAML frontmatter + markdown)

Key Rules:
  - Manager CANNOT implement (strict separation)
  - Context-scoped agents (each gets only relevant info)
  - Same-agent deps = lightweight reference
  - Cross-agent deps = comprehensive integration context
  - Handover blocked during active task execution
  - Ad-hoc agents work in separate branches, no Memory logging
```
