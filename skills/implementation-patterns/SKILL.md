---
name: implementation-patterns
description: Code implementation methodology — pattern reuse, test-first development, phased execution, and quality verification
user-invocable: false
---

# Implementation Patterns

Follow every section in order.

## 1. Pattern Discovery (Before Writing Code)

Before creating ANY new code, search the codebase:

- **Similar features** — Search for components/services solving related problems. Grep domain terms.
- **Conventions** — Naming (camelCase/snake_case), file naming, directory structure, error handling, logging.
- **Documented patterns** — Check `docs/solutions/` for authoritative architecture decisions.
- **Test conventions** — Read 2-3 test files: framework, assertion style, naming (`*.test.ts`/`*.spec.ts`), mocking.
- **DESIGN.md** — If exists, use D-R{n} specs exactly: tokens, spacing, type ramps, component specs.
- **TECHNICAL.md** — If exists, follow T-R{n} specs exactly: API schemas, data models, error contracts, ADRs.

Build a mental model: "In this project, a [feature type] is built by creating [files] in [locations] following [pattern], tested with [framework] using [conventions]."

## 2. Test-First Implementation

Write tests BEFORE implementation when possible.

- Put tests where the project puts them. Use same framework, style, naming.
- **Pure logic** — Test input/output pairs + edge cases. Mock nothing.
- **API/DB** — Test request/response + persistence + errors. Mock only external services.
- **UI** — Test render + interactions + edge states. Mock API calls + timers.

Every Given/When/Then from SPEC.md maps to ≥1 test. Don't mock what you can test directly. If mocking 3+ things, the code needs refactoring.

## 3. Implementation Order

Within a phase, implement in this order:
1. **Data layer** — Models, schemas, types, migrations
2. **Business logic** — Services, utilities, validators
3. **Interface layer** — API routes, UI components
4. **Integration** — Wiring, route registration, store connections

Each layer tested independently before integration. If PLAN.md specifies different order, follow the plan.

## 4. Code Quality Gates

After each completed function/component/module:
1. Run the specific test (not full suite)
2. Run linter/formatter
3. Run type-checker
4. Fix failures immediately — don't accumulate

If a gate fails twice on same issue, stop and reassess the approach.

## 5. Phased Execution

From PLAN.md:
1. Read entire phase first — scope, files, tasks, test gate
2. Mark `**Status: in progress**` in PLAN.md
3. Execute tasks in order (sequenced intentionally)
4. Run phase test gate after all tasks
5. Mark `**Status: complete**` only after gate passes
6. If gate fails twice, stop and report: failing test, error, hypothesis, what you tried

Don't continue to next phase with a failing gate.

## 6. Parallel Phase Execution

When `Parallel: yes` in PLAN.md:
- Implement in separate worktree/context to avoid conflicts
- After all complete, verify integration
- Run full test suite after merging — check for unintended interactions

## 7. Code Reuse Rules

- **80% match** — Extend existing utility, don't create parallel implementation
- **Placement** — Shared (`utils/`, `lib/`) if used by 2+ modules, local otherwise
- **Abstraction level** — Match the project's style
- **Extraction at 3** — Copy-paste OK for 1-2 occurrences, extract at 3+

## 8. Error Handling Patterns

- **Match project approach** — Exceptions, Result types, or error codes — whatever the project uses
- **Validate at boundaries** — User input, API responses, env vars, file reads, external calls
- **Trust internal code** — No defensive null checks for your own return values
- **Actionable messages** — What went wrong + what to do. Not `"Invalid input"` → `"Email must contain @ — received 'not-an-email'"`
- **Never swallow errors** — No empty catch blocks. At minimum, log. Prefer surfacing.

## 9. Commit Hygiene

- Commit at phase boundaries, after test gate passes
- One commit per phase, atomic and reviewable
- Message: `feat: implement [phase name] (Phase N)`
- Never commit with failing tests/lint/type errors

## 10. When Stuck

1. Re-read the error message carefully
2. Search for similar working code in the project
3. Verify assumptions — log intermediate values
4. After 2 failed attempts, STOP and report what you tried + hypothesis
5. Consider if spec/plan needs updating — flag ambiguity rather than guessing
