---
name: implementation-patterns
description: Code implementation methodology — pattern reuse, test-first development, phased execution, and quality verification
user-invocable: false
---

# Implementation Patterns

This skill defines how to implement features methodically. Follow every section in order.

## 1. Pattern Discovery (Before Writing Code)

Before creating ANY new code, search the codebase systematically:

- **Similar features:** Search for components, modules, or services that solve a related problem. Use file names, directory structure, and grep for domain terms. If you're building a "notification service," search for existing services to understand the pattern.
- **Project conventions:** Identify naming conventions (camelCase vs snake_case, file naming like `user-service.ts` vs `UserService.ts`), directory structure (where do services live? where do tests live?), error handling patterns, and logging approach.
- **Documented patterns:** Check `docs/solutions/` for architectural decisions or pattern documentation. These are authoritative -- follow them over what you infer from code.
- **Test conventions:** Read 2-3 existing test files to understand the testing framework, assertion style, file naming (`*.test.ts` vs `*.spec.ts`), mocking approach, and setup/teardown patterns.
- **Design tokens:** If DESIGN.md exists, read the D-R{n} specs. They contain concrete values (color tokens, spacing scales, type ramps, component schemas, API endpoint shapes) that must be used exactly as specified. Do not improvise values that are defined in DESIGN.md.

Build a mental model before writing anything: "In this project, a [feature type] is built by creating [files] in [locations] following [pattern], tested with [framework] using [conventions]."

## 2. Test-First Implementation

For each task, write the test BEFORE the implementation when possible.

### Test structure must match the project

- Put test files where the project puts them (co-located, `__tests__/`, `tests/`, etc.)
- Use the same framework and assertion style as existing tests
- Follow the same naming pattern for test files and test descriptions

### Types of tests to write

| Layer | What to test | What to mock |
|---|---|---|
| Pure logic (functions, transformers, validators) | Input/output pairs, edge cases, error conditions | Nothing -- these are pure |
| API endpoints / database operations | Request/response cycle, data persistence, error responses | External services only |
| UI components | Render output, user interactions, edge states (empty, loading, error) | API calls, timers, external dependencies |

### Mapping acceptance criteria to tests

Every acceptance criterion from SPEC.md (Given/When/Then) must map to at least one test:

```
// SPEC.md says:
// Given a user with 3 items, when they delete the second item,
// then the list shows 2 items and a success toast appears.

test("deleting an item removes it from the list and shows success toast", () => {
  // Given
  const items = setupItemList(3);
  // When
  deleteItem(items, 1);
  // Then
  expect(getVisibleItems()).toHaveLength(2);
  expect(getToast()).toEqual({ type: "success", visible: true });
});
```

### Mocking rules

- Don't mock what you can test directly -- only mock external services and I/O boundaries
- If you find yourself mocking 3+ things in a single test, the code under test probably needs refactoring
- Use the project's existing mock utilities and patterns before creating new ones

## 3. Implementation Order

Within a phase, implement layers in this order:

1. **Data layer first** -- models, schemas, types, migrations, database queries
2. **Business logic second** -- services, utilities, transformers, validators
3. **Interface layer third** -- API routes, UI components, CLI handlers
4. **Glue/integration last** -- wiring layers together, registering routes, connecting stores to components

This order ensures each layer can be tested independently before integration. If the data layer is wrong, you find out before building UI on top of it.

**Exception:** If PLAN.md specifies a different order within a phase, follow the plan. The plan was written with project-specific context.

## 4. Code Quality Gates

After each logical unit of work (not each line -- each completed function, component, or module):

1. **Run the specific test** for what you just wrote or changed. Not the full suite -- just the relevant tests.
2. **Run the linter/formatter** if the project has one configured (check `package.json` scripts, `pyproject.toml`, `Makefile`, or CI config).
3. **Run type-checking** if the project uses TypeScript (`tsc --noEmit`), mypy, or similar.
4. **Fix failures immediately.** Do not proceed to the next task with a failing test, lint error, or type error. Accumulating failures makes root causes harder to find.

If a quality gate fails twice on the same issue, stop and reassess. The approach may be wrong, not just the code.

## 5. Phased Execution

When implementing from PLAN.md:

1. **Read the entire phase** before starting -- scope, files, tasks, and test gate. Understand what "done" looks like for this phase.
2. **Mark the phase** as `**Status: in progress**` in PLAN.md when starting.
3. **Execute tasks in order.** They are sequenced intentionally -- earlier tasks create foundations that later tasks build on.
4. **Run the phase's test gate** after all tasks in the phase are complete. The test gate is the definition of done, not task completion.
5. **Mark as `**Status: complete**`** only after the test gate passes.
6. **If the test gate fails twice**, stop and report:
   - Which specific test/check is failing
   - The error message or output
   - Your hypothesis for why it's failing
   - What you've already tried

Do not continue to the next phase with a failing test gate. Phases build on each other.

## 6. Parallel Phase Execution

When phases are marked `Parallel: yes` in PLAN.md:

- These phases have no dependencies on each other and can run concurrently
- Each parallel phase should be implemented in its own worktree or context to avoid file conflicts
- After all parallel phases complete, verify they integrate correctly together
- Run the full test suite after merging parallel work -- parallel phases may have unintended interactions
- If parallel phases modify the same file, resolve conflicts carefully and re-run both phases' test gates

## 7. Code Reuse Rules

- **80% match:** If you find an existing utility that does 80%+ of what you need, extend it rather than creating a new one. Add parameters or configuration, not a parallel implementation.
- **Placement:** If you create a new utility, check if it belongs in a shared location (`utils/`, `lib/`, `shared/`, `common/`). If it's used by one module, keep it local. If it's used by two or more, move it to shared.
- **Abstraction level:** Match the project's abstraction level. If existing code is explicit and procedural, don't introduce an abstract factory pattern. If existing code uses dependency injection, follow that pattern.
- **Extraction threshold:** Copy-paste is acceptable for 1-2 occurrences. At 3+, extract to a shared function or component. When extracting, make sure all existing call sites use the extracted version.

## 8. Error Handling Patterns

- **Match the project's approach.** If the project throws exceptions, throw exceptions. If it uses Result types, use Result types. If it returns error codes, return error codes. Don't introduce a new error handling paradigm.
- **Validate at boundaries.** User input, API responses, environment variables, file reads, external service calls -- validate these. Use schemas (Zod, Pydantic, JSON Schema) when available in the project.
- **Trust internal code.** Don't add defensive null checks for values your own code produces. If `getUserById` returns a user (not null), the caller doesn't need `if (user)`.
- **Actionable messages.** Error messages should answer two questions: what went wrong, and what to do about it. Bad: `"Invalid input"`. Good: `"Email address must contain @ -- received 'not-an-email'"`.
- **Never swallow errors silently.** Empty catch blocks, bare `except:` clauses, and `.catch(() => {})` are bugs. At minimum, log the error. Prefer surfacing it to the caller.

## 9. Commit Hygiene During Implementation

- **Commit at phase boundaries.** Don't commit mid-phase with partial work. Commit after the phase's test gate passes.
- **One commit per phase.** Each commit should be atomic and independently reviewable. If someone reverts your commit, one complete phase disappears cleanly.
- **Reference the phase in the commit message:** `feat: implement [phase name] (Phase N)`
- **If a phase is large,** it's acceptable to commit at natural sub-boundaries (e.g., data layer done, then business logic done), but each sub-commit must still pass its relevant tests.
- **Never commit with failing tests, lint errors, or type errors.** The main branch must always be in a working state.

## 10. When You're Stuck

If you hit a wall during implementation:

1. **Re-read the failing test or error message carefully.** The answer is often in the output.
2. **Check if the pattern exists elsewhere.** Search for similar code that already works in the project.
3. **Verify your assumptions.** Print/log intermediate values. Check that the data layer returns what you expect before debugging the UI.
4. **After 2 failed attempts, stop.** Report what you tried, what happened, and your hypothesis. Don't keep trying variations of the same approach -- step back and reassess.
5. **Consider if the spec or plan needs updating.** Sometimes implementation reveals that a requirement is ambiguous or a plan step is missing. Flag it rather than guessing.
