---
name: debugging-methodology
description: Systematic debugging methodology — hypothesis-driven root cause analysis, bisection strategies, and regression prevention
user-invocable: false
---

# Debugging Methodology

Follow this methodology for every bug investigation. Do not skip steps.

## 1. Error Classification

Before investigating, classify the error to choose the right strategy:

| Type | Signals | Strategy |
|---|---|---|
| **Crash/Exception** | Stack trace, error message, process exit | Start from the stack trace, work backwards through the call chain |
| **Wrong Output** | Tests fail, incorrect data, unexpected behavior | Compare expected vs actual, find the divergence point |
| **Performance** | Slow responses, timeouts, high memory/CPU | Profile first, measure before and after |
| **Intermittent** | Works sometimes, fails sometimes | Look for race conditions, state leaks, timing dependencies, external service flakiness |
| **Regression** | Worked before, broke after a change | Use git bisect or manual binary search through recent commits |
| **Silent Failure** | No error, but feature doesn't work | Check for swallowed errors, missing error handlers, early returns |

## 2. Evidence Collection (Before Forming Hypotheses)

Gather facts before theorizing. Do ALL of the following:

- Read the FULL error message and stack trace -- not just the first line
- Reproduce the error reliably. If you cannot reproduce it, document the conditions under which it was reported
- Check: when did this last work? What changed since then? (`git log --oneline -10`)
- Check: does this fail in all environments or just one? (dev vs test vs prod)
- Check `docs/solutions/` for similar past issues and their root causes
- Check agent memory for patterns you have seen before in this codebase
- Collect relevant log output, test output, and error messages verbatim

## 3. Hypothesis-Driven Investigation

Form 2-3 hypotheses ranked by likelihood BEFORE reading code:

```
H1: [Root cause theory]
Evidence for: [what supports this theory]
Evidence against: [what contradicts it]
Test: [specific action to confirm or eliminate]
```

Rules:
- Test the MOST LIKELY hypothesis first
- Each test must definitively confirm or eliminate the hypothesis
- Do not read code aimlessly -- read the specific files your hypothesis points to
- If H1 is eliminated, update your understanding before testing H2
- If all hypotheses are eliminated, return to evidence collection -- you missed something

## 4. Debugging Strategies by Type

### Stack Trace Analysis

1. Start at the top of the stack trace (the error site)
2. Read the function that threw the error
3. Identify the specific line and variable that is wrong
4. Trace backwards: where did that variable get its value?
5. Continue up the call chain until you find where correct data became incorrect
6. The bug is at the transition point, not at the error site

### Binary Search (Bisection)

When you know it worked before but do not know which change broke it:

1. Find a known-good commit and a known-bad commit
2. Test the midpoint
3. Narrow the range by half each time
4. In 10 iterations, you can search 1024 commits

Use `git bisect start`, `git bisect good [ref]`, `git bisect bad [ref]` for automated bisection. Combine with a test command: `git bisect run [test-command]`.

### Data Flow Tracing

When output is wrong but no error is thrown:

1. Identify the entry point (where data enters the system)
2. Add logging or assertions at each transformation point
3. Find the FIRST point where data diverges from expectations
4. That transformation is the bug -- not the final output
5. Remove debug logging after finding the issue

### State Inspection

For intermittent bugs or state-related issues:

1. List ALL mutable state the code touches (variables, database, cache, session, globals)
2. For each piece of state: what is its value at the point of failure?
3. What SHOULD its value be?
4. Who else modifies this state? (search for all writes to that variable/table/key)
5. Is there a race condition? (two code paths modifying the same state concurrently)
6. Is there a state leak? (state from a previous operation contaminating the current one)

## 5. The Minimal Fix

After finding the root cause:

- Fix the ROOT CAUSE, not the symptom. If a null check would "fix" it, ask: why is it null? Fix that instead
- The fix should be the SMALLEST change that resolves the issue
- Do not refactor, rename, or "improve" surrounding code in the same fix
- If the fix requires a larger refactor, document that as a separate follow-up task with an issue
- Verify the fix addresses the root cause, not just the specific failing case

## 6. Regression Prevention

After implementing the fix:

1. Write a test that FAILS without the fix and PASSES with it
2. The test should test the ROOT CAUSE scenario, not just the symptom
3. Name the test descriptively: `test_[thing]_[scenario]_[expected_behavior]`
4. Run the specific test file to confirm the new test passes
5. Run the full test suite to ensure no regressions from the fix
6. If the bug was in a pattern that exists elsewhere, search for and fix all instances

## 7. Root Cause Report

Document every non-trivial fix with this structure:

```markdown
## Root Cause
[One sentence: what was actually wrong]

## Evidence
[How you confirmed this was the cause, not just a correlation]

## Fix
[What was changed and why this addresses the root cause]

## Prevention
[How to prevent similar bugs: conventions, linting rules, type constraints, tests]
```

Store reports in `docs/solutions/` so future investigations can reference them.

## 8. Anti-Patterns (Do NOT Do These)

- **Shotgun debugging**: Changing things randomly until it works. You learn nothing and may introduce new bugs
- **Symptom suppression**: Adding try/catch, null checks, or defaults that hide the real problem
- **Blame-driven debugging**: Assuming the bug is in someone else's code or a library. Verify your code first before escalating
- **Tunnel vision**: Fixating on one hypothesis despite evidence against it. Step back and reconsider after a failed test
- **Over-investigation**: Spending hours on a minor issue. Use the 2-attempt rule: if two hypotheses fail, stop and re-plan with what you have learned
- **Aimless code reading**: Scrolling through files hoping to spot the bug. Always have a hypothesis guiding what you read
- **Fix-and-forget**: Fixing the bug without writing a regression test. The same bug will return
- **Scope creep**: Refactoring or cleaning up code you encounter while debugging. File a separate issue instead
