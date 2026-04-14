---
paths: ["src/api/**", "app/api/**", "routes/**", "server/**", "backend/**"]
---
<!-- astra:managed -->
- Follow existing route patterns for new endpoints (naming, HTTP verbs, response envelope).
- All endpoints must validate input at the boundary (Zod, Joi, Pydantic, etc.).
- Error responses must use the project's error envelope format.
- New endpoints require integration tests covering success + error cases.
- Authentication/authorization checked on every protected route.
- No sensitive data in error messages (stack traces, DB schemas, file paths).
