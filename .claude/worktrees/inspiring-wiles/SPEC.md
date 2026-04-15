Before I write the spec, I need to validate my interpretation and nail down scope. Here are my discovery questions:

**1. What does "test auth" mean here?**

I see an untested auth/permissions system across 4 files (`permissions.py`, `hooks.py`, `config.py`, `mcp.py`). Which do you mean:

- **A) Test existing auth system** — Build a comprehensive test suite for the permission hooks, token loading, path restrictions, and audit trail that already exist but have zero tests
- **B) Build a new auth feature** — Design a new authentication layer (user login, API key management, session tokens) that doesn't exist yet
- **C) Both — test + harden** — Test existing code AND spec improvements like token validation, missing-token errors, secret rotation

**2. Priority components?**

- Permission hooks (`enforce_readonly`, `enforce_path_restrictions`) — the security boundary
- Token/config loading (`AstraConfig` env vars, `has_github()`)
- Audit trail integrity (JSONL logging)
- All of the above

**3. Test depth?**

- **Unit only** (recommended: fast, isolated, <5s, covers pure logic)
- **Unit + integration** (hook→SDK→permission chain with fixtures, ~30s)
- **Unit + integration + E2E** (full pipeline stage with enforcement)

These answers will shape whether the spec is 8 requirements or 25. What's your intent?