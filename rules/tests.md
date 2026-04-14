---
paths: ["**/*.test.*", "**/*.spec.*", "tests/**", "test/**", "__tests__/**"]
---
<!-- astra:managed -->
- Follow existing test framework and assertion style (read 2-3 existing test files first).
- Test behavior (what the code does) not implementation (how it does it).
- Each test must be independent — no shared mutable state between test cases.
- Include edge cases and error paths, not just the happy path.
- Assertions must be specific (exact values), not vague (truthy/falsy).
- Never weaken existing tests to make them pass.
