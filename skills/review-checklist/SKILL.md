---
name: review-checklist
description: Comprehensive code review checklist covering security, performance, quality, reusability, tech debt, accessibility, and API design
user-invocable: false
---

# Code Review Checklist

Apply every section to the code under review. For each item, answer yes/no. Flag any "no" as a finding.

## Security

- Are user inputs validated at the system boundary (API handlers, form submissions)?
- Are SQL queries parameterized (no string concatenation or f-strings in queries)?
- Are secrets stored in environment variables, not hardcoded in source?
- Is authentication checked on every protected route/endpoint?
- Are error messages free of internal details (stack traces, DB schemas, file paths)?
- Is user-uploaded content sanitized before storage and rendering?
- Are CORS, CSP, and other security headers configured correctly?
- Is authorization checked (not just authentication) — can user A access user B's data?

## Performance

- Are database queries using appropriate indexes for the access pattern?
- Are there N+1 query patterns (loop that issues a query per iteration)?
- Are large lists paginated (not fetching all records at once)?
- Are expensive computations cached where the data doesn't change frequently?
- Are there unnecessary re-renders in frontend components (missing memo, key, or dependency arrays)?
- Are file reads, network calls, or DB queries happening in hot paths that could be deferred?
- Are large payloads being sent when only a subset of fields is needed?

## Quality

- Does every function/method do one thing with a clear name?
- Are variable and function names descriptive enough to understand without comments?
- Are edge cases handled: null, undefined, empty arrays, zero, negative numbers, boundary values?
- Do error paths have appropriate handling (not silently swallowed)?
- Are there magic numbers or strings that should be named constants?
- Is the code free of unreachable code, dead branches, or unused imports?
- Are types correct and specific (no `any` in TypeScript, no `# type: ignore` without explanation)?

## Reusability

- Does this change reimplement something that already exists in the codebase?
- Are there 3+ instances of the same pattern that should now be extracted into a shared utility?
- Are new utilities and helpers placed where other modules can reach them?
- Does the new code follow the existing patterns and conventions of the project?

## Tech Debt

- Does this change introduce new TODOs without linked issues or a clear plan?
- Is there any commented-out code that should be removed?
- Are deprecated APIs or patterns used where current alternatives exist?
- Are there hardcoded values (URLs, limits, feature flags) that should be configuration?
- Is test coverage adequate for the changed code paths?
- Are there any `// eslint-disable`, `# noqa`, or similar suppressions without explanation?

## Testing

- Do tests verify behavior (what the code does) not implementation (how it does it)?
- Are assertions specific (exact values) not vague (truthy/falsy)?
- Are edge cases and error paths tested, not just the happy path?
- Are tests independent — no shared mutable state between test cases?
- Were any existing tests weakened (assertions removed or loosened) to make them pass?

## Accessibility (if frontend changes)

- Do interactive elements (buttons, links, inputs) have accessible names (aria-label, visible text, or associated label)?
- Is keyboard navigation supported — can all interactive elements be reached and activated without a mouse?
- Do images have meaningful alt text (or empty alt="" for decorative images)?
- Is color contrast sufficient (at least 4.5:1 for normal text, 3:1 for large text)?
- Are ARIA roles and attributes used correctly (not overriding native semantics)?
- Do form fields have associated `<label>` elements or `aria-labelledby`?

## API Design (if API changes)

- Are endpoints RESTful and consistent with existing API patterns (naming, HTTP verbs, status codes)?
- Do API responses use consistent envelope/shape with existing endpoints?
- Are request payloads validated and documented (expected types, required vs optional fields)?
- Are error responses structured consistently (error code, message, details)?
- Is pagination, filtering, and sorting handled for list endpoints?
- Are breaking changes avoided, or versioned if unavoidable?
