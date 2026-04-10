---
name: technical-architecture
description: Technical design methodology — API contracts, data models, system architecture, ADRs, and error handling
user-invocable: false
---

# Technical Architecture Methodology

This skill defines how to produce technical design documents. Every technical design must follow this methodology exactly. The output is `TECHNICAL.md` — a companion to DESIGN.md (which covers UI/UX). All elements trace back to SPEC.md requirements using the `T-R{n}` prefix.

---

## 1. Existing System Discovery

Before designing anything, explore the codebase for existing technical patterns. This is mandatory.

**Search these file patterns:**

| Pattern | What to find |
|---|---|
| `routes/`, `app/api/`, `pages/api/`, `src/api/` | API route definitions |
| `prisma/schema.prisma`, `drizzle/`, `models/`, `entities/` | Data models and ORM schemas |
| `migrations/`, `prisma/migrations/`, `alembic/` | Migration history and naming conventions |
| `middleware/`, `src/middleware/` | Auth, validation, error handling middleware |
| `lib/errors`, `utils/errors`, `exceptions/` | Error handling patterns |
| `tests/integration/`, `__tests__/api/`, `spec/requests/` | Integration test structure |
| `.env.example`, `config/` | Environment variables and service dependencies |
| `docker-compose.yml`, `Dockerfile` | Infrastructure and service boundaries |

**Document these findings before proceeding:**

- **API patterns** — REST or GraphQL? Response envelope format (e.g., `{ data, error, meta }`). Auth mechanism (JWT, session, API key). Naming conventions (camelCase vs snake_case in payloads).
- **Data layer** — ORM (Prisma, Drizzle, SQLAlchemy, TypeORM). Database type (Postgres, MySQL, SQLite). Migration tool and naming convention. Column naming (snake_case vs camelCase). Soft delete pattern (if any).
- **Service boundaries** — Monolith or microservices? Message queue? Event bus? External API integrations with their client libraries.
- **Error handling** — How errors propagate from service layer to API response. Logging library and approach. Error codes or error types in use.
- **Testing** — Integration test framework. How API tests are structured (setup, request, assertion). Database seeding/fixture approach.

The goal: extend existing patterns, never reinvent them.

---

## 2. Architecture Decision Records

For every non-trivial technical decision, create an ADR using the MADR format. A decision is non-trivial if it involves: a new database table, a new external dependency, choosing between frameworks or libraries, authentication strategy, caching strategy, or a breaking API change.

**Format per ADR:**

```
### ADR-{n}: [Decision Title]
**Status:** Proposed | Accepted | Superseded
**Context:** [Why this decision is needed — the forces at play]
**Options considered:**
- Option A: [description] — Pros: [...] Cons: [...]
- Option B: [description] — Pros: [...] Cons: [...]
- Option C: [description] — Pros: [...] Cons: [...]
**Decision:** [Which option and why]
**Consequences:** [What follows — both positive and negative]
**Traces to:** R{n}, D-R{n}
```

**Rules:**
- Minimum two options per ADR. "Do nothing" counts as an option.
- Every ADR must trace to at least one SPEC.md requirement.
- Status starts as Proposed. The calling agent or user promotes to Accepted.
- If a later decision supersedes an earlier one, mark the old ADR as `Superseded by ADR-{n}`.

---

## 3. API Contract Design

Follow a three-phase approach: Domain analysis, Resource definition, Contract specification.

**Phase 1 — Domain analysis:** Identify the domain entities and actions from SPEC.md requirements. Map each requirement to one or more API operations.

**Phase 2 — Resource definition:** Define REST resources (nouns, not verbs). Determine resource hierarchy and URL structure consistent with existing routes.

**Phase 3 — Contract specification:** For each endpoint, specify all of the following:

```
### T-R{n}: [Endpoint Name]
**Traces to:** R{n}
**Method:** GET | POST | PUT | PATCH | DELETE
**Path:** /api/v{n}/resource
**Auth:** Public | Authenticated | Role(admin, editor)
**Request:**
  Content-Type: application/json
  {
    "field": "string (required, min: 1, max: 255)",
    "count": "integer (optional, default: 10, min: 1, max: 100)"
  }
**Response (success):**
  Status: 200 | 201 | 204
  {
    "data": { ... },
    "meta": { "page": 1, "total": 42 }
  }
**Response (error):**
  Status: 400 | 401 | 403 | 404 | 409 | 422
  {
    "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] }
  }
**Rate limit:** {n} requests per {window}
```

**Additional API rules:**
- **Pagination** — Detect existing strategy (cursor-based vs offset). If none exists, prefer cursor-based for large datasets, offset for small. Document the pagination envelope.
- **Versioning** — Match existing approach (URL path `/v1/`, header, query param). If none exists, use URL path versioning.
- **Idempotency** — POST/PUT endpoints that create resources should document idempotency keys if applicable.
- **Field validation** — Every request field must have type, required/optional, and at least one constraint (min, max, pattern, enum).

---

## 4. Data Model Design

For each entity, specify all of the following:

**Fields table:**

| Field | Type | Constraints | Default | Purpose |
|---|---|---|---|---|
| id | uuid | PK, NOT NULL | gen_random_uuid() | Primary identifier |
| name | varchar(255) | NOT NULL, UNIQUE | — | Display name |
| created_at | timestamptz | NOT NULL | now() | Audit trail |

**Relationships:**
- `Order belongs_to User` via `user_id` FK — ON DELETE CASCADE
- `Order has_many OrderItems` via `order_id` FK — ON DELETE CASCADE

**Indexes:**

| Index | Type | Columns | Justification |
|---|---|---|---|
| idx_orders_user_id | btree | user_id | Query: list orders by user |
| idx_orders_created_at | btree | created_at DESC | Query: recent orders dashboard |
| uq_users_email | unique | email | Constraint: unique email |

**Additional data model rules:**
- **Migrations** — State whether each change is additive (safe to deploy) or breaking (requires coordination). Include rollback plan for breaking changes.
- **Soft delete vs hard delete** — Decide per entity and document rationale. If the entity has audit requirements or FK dependencies, prefer soft delete.
- **Seed data** — List any reference data, lookup tables, or test fixtures needed.
- **Entity relationship summary** — A text-based summary of how entities relate (one paragraph).

---

## 5. System Architecture / Flow

For each major operation, write a component-level sequence showing the full request lifecycle:

```
1. Client sends POST /api/orders with payload
2. API gateway: rate limit check
3. Auth middleware: validate JWT, extract user context
4. Validation layer: validate request body (Zod/Joi schema)
5. Service layer: check inventory availability
6. Database: BEGIN TRANSACTION
7. Database: INSERT into orders
8. Database: UPDATE inventory (decrement stock)
9. Database: COMMIT
10. Event emitted: OrderCreated → notification service
11. Response: 201 Created with order object
```

**For each sequence, also document:**

- **Error propagation paths** — What happens when step N fails? Example: "If step 8 fails (insufficient stock), ROLLBACK transaction, return 409 Conflict with error code `INSUFFICIENT_STOCK`."
- **Transaction boundaries** — Which steps are within a transaction? What is the isolation level?
- **External dependency map** — List every external service/API called, with failure mode and fallback. Example: "Payment gateway (Stripe) — timeout after 10s, retry 2x, then return 503 with `PAYMENT_UNAVAILABLE`."

---

## 6. Error Handling Taxonomy

Classify all errors into these categories and define handling for each:

| Category | Status | Error Code Format | Log Level | Retry |
|---|---|---|---|---|
| Validation | 400 | `VALIDATION_{FIELD}` | warn | No |
| Authentication | 401 | `AUTH_REQUIRED` | warn | No |
| Authorization | 403 | `FORBIDDEN_{RESOURCE}` | warn | No |
| Not found | 404 | `{RESOURCE}_NOT_FOUND` | info | No |
| Conflict | 409 | `{RESOURCE}_{CONFLICT}` | warn | No |
| Business rule | 422 | `{RULE}_VIOLATED` | warn | No |
| System error | 500 | `INTERNAL_ERROR` | error | No |
| External service | 502/503 | `{SERVICE}_UNAVAILABLE` | error | Yes |

**Error response envelope** — Must match the existing project pattern. If none exists, use:

```json
{
  "error": {
    "code": "VALIDATION_EMAIL",
    "message": "Email address is invalid",
    "details": [
      { "field": "email", "rule": "format", "message": "Must be a valid email" }
    ]
  }
}
```

**Retry strategy for transient errors:**
- Which errors: 502, 503, network timeouts, database connection failures
- Max retries: 3
- Backoff: exponential (1s, 2s, 4s) with jitter
- Circuit breaker threshold: 5 failures in 60s opens circuit for 30s

---

## 7. Security Considerations

**Auth flow** — Detect from codebase (JWT, session cookies, OAuth 2.0, API keys). Document:
- Token issuance and refresh mechanism
- Token storage approach (httpOnly cookie, memory, localStorage)
- Session expiry and renewal strategy

**Input validation boundaries:**
- Where validation happens (API layer, service layer, database constraints)
- What each layer enforces (schema shape, business rules, data integrity)
- Sanitization for injection prevention (SQL, XSS, command injection)

**Data protection:**
- Fields requiring encryption at rest (PII, secrets, tokens)
- TLS requirements for data in transit
- Data retention and purging policy

**Audit logging:**
- Which operations are logged (create, update, delete of sensitive resources)
- Log format: `{ actor, action, resource, resourceId, timestamp, metadata }`
- Storage and retention period

**Rate limiting:**
- Per-endpoint limits (auth endpoints stricter than read endpoints)
- Global rate limit per API key / user
- Rate limit response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`)

**CORS configuration:**
- Allowed origins (detect from existing config)
- Allowed methods and headers
- Credentials policy

---

## 8. Performance Considerations

**Caching strategy:**

| What to cache | Where | TTL | Invalidation trigger |
|---|---|---|---|
| User profile | In-memory / Redis | 5 min | User update event |
| Config/settings | Application memory | 15 min | Admin update + restart |
| API response | CDN / edge | 60s | Cache-Control header |

**Query optimization:**
- N+1 prevention: specify eager loading for known relationship queries
- Identify queries needing pagination (any query returning unbounded results)
- Indexes justified by specific query patterns (see Data Model section)

**Payload and connection management:**
- Request payload size limit (e.g., 1MB default, 10MB for file uploads)
- Response payload size considerations (pagination, field selection)
- Database connection pool size and timeout settings
- HTTP keep-alive and timeout configuration

**Async operations:**
- Which operations should be queued (email, webhooks, report generation, heavy computation)
- Queue technology (detect from codebase or recommend based on ADR)
- Job retry and dead-letter policy

---

## 9. Traceability

Every technical design element uses the `T-R{n}` prefix, tracing back to SPEC.md requirements:

- API endpoints: `T-R1: POST /api/orders` traces to R1
- Data models: `T-R2: orders table` traces to R2
- ADRs: `ADR-1` traces to R3 (via the Traces to field)
- Multiple elements per requirement: `T-R1a: POST /api/orders`, `T-R1b: orders table`

A single element CAN map to multiple requirements (e.g., `T-R1,R3: orders service`), and a single requirement CAN produce multiple elements.

**Traceability Matrix:**

| Requirement | Technical Element(s) | Type |
|---|---|---|
| R1 | T-R1a: POST /api/orders | API Endpoint |
| R1 | T-R1b: orders table | Data Model |
| R2 | T-R2: GET /api/orders | API Endpoint |
| R3 | ADR-1: Database choice | Decision |

If any R{n} from SPEC.md has no corresponding T-R{n}, the design is incomplete.

---

## 10. TECHNICAL.md Output Template

Write the final technical design to `TECHNICAL.md` in the project root. Use this exact structure:

```markdown
# Technical Design: [Feature Name]

**Last revised:** [date] — [one-line summary if revised]

## Existing System Patterns
- API style: [REST / GraphQL, envelope format, auth mechanism]
- Data layer: [ORM, database, migration tool]
- Error handling: [pattern, logging approach]
- Testing: [framework, integration test structure]

## Architecture Decision Records

### ADR-1: [Title]
**Status / Context / Options / Decision / Consequences / Traces to**

## API Contracts

### T-R{n}: [Endpoint Name]
**Traces to:** R{n}
**Method / Path / Auth / Request / Response / Errors / Rate limit**

## Data Model

### T-R{n}: [Entity Name]
**Traces to:** R{n}
Fields table + Relationships + Indexes + Migration notes

## System Architecture
### [Operation Name] Flow
Numbered sequence + error paths + transaction boundaries

## Error Handling
Error taxonomy table + response envelope + retry strategy

## Security
Auth flow + validation boundaries + encryption + audit + rate limits + CORS

## Performance
Caching table + query optimization + payload limits + async operations

## Traceability Matrix
| Requirement | Technical Element(s) | Type |
|---|---|---|
| R{n} | T-R{n}: [element] | [type] |
```

---

## 11. Validation Checklist

Before finalizing the technical design, verify every item:

- [ ] Every R{n} from SPEC.md has at least one T-R{n} element
- [ ] Traceability Matrix is complete — no requirement left unmapped
- [ ] All API endpoints have complete request and response schemas with types and constraints
- [ ] All data model entities have fields, types, constraints, and relationships defined
- [ ] ADRs exist for every non-trivial decision (new tables, new dependencies, framework choices)
- [ ] Error handling covers all endpoint failure modes with status codes and error codes
- [ ] Security section addresses auth flow, input validation, and sensitive data protection
- [ ] Performance section addresses caching strategy and query optimization patterns
- [ ] System architecture sequences include error propagation paths
- [ ] Existing codebase patterns are referenced by file path, not reinvented
- [ ] All design elements use `T-R{n}` prefix with correct requirement traces
- [ ] Migration plan distinguishes additive vs breaking changes with rollback strategy
