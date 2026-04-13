---
name: technical-architecture
description: Technical design methodology — API contracts, data models, system architecture, ADRs, and error handling
user-invocable: false
---

# Technical Architecture Methodology

Produces `TECHNICAL.md` — companion to DESIGN.md (UI/UX). All elements trace to SPEC.md requirements using `T-R{n}`. Follow every section.

## 1. Existing System Discovery

Before designing, explore the codebase for existing patterns. Mandatory.

**Search:** `routes/`, `app/api/` (API routes), `prisma/`, `models/`, `entities/` (data models), `migrations/` (naming conventions), `middleware/` (auth, validation, errors), `lib/errors` (error patterns), `tests/integration/` (test structure), `.env.example` (service deps).

**Document before proceeding:**
- **API patterns** — REST/GraphQL, response envelope, auth mechanism, naming (camelCase/snake_case)
- **Data layer** — ORM, database type, migration tool, column naming, soft delete pattern
- **Service boundaries** — Monolith/microservices, message queues, external integrations
- **Error handling** — Propagation from service to API response, logging library, error codes
- **Testing** — Framework, API test structure, DB seeding approach

Goal: extend existing patterns, never reinvent.

## 2. Architecture Decision Records

For non-trivial decisions (new tables, external deps, framework choices, auth strategy, caching, breaking API changes), create ADR:

```
### ADR-{n}: [Title]
**Status:** Proposed | Accepted | Superseded
**Context:** [Why needed — forces at play]
**Options:**
- A: [desc] — Pros: [...] Cons: [...]
- B: [desc] — Pros: [...] Cons: [...]
**Decision:** [Which and why]
**Consequences:** [Positive + negative]
**Traces to:** R{n}
```

Rules: ≥2 options per ADR. "Do nothing" counts. Every ADR traces to ≥1 requirement.

## 3. API Contract Design

Three phases: Domain analysis → Resource definition → Contract specification.

Per endpoint:
```
### T-R{n}: [Endpoint Name]
**Traces to:** R{n}
**Method:** GET | POST | PUT | PATCH | DELETE
**Path:** /api/v{n}/resource
**Auth:** Public | Authenticated | Role(admin)
**Request:** { "field": "string (required, min:1, max:255)" }
**Response (success):** Status + schema
**Response (error):** Status + error envelope
**Rate limit:** {n}/window
```

Rules:
- **Pagination** — Match existing (cursor vs offset). Default cursor for large datasets.
- **Versioning** — Match existing. Default URL path (`/v1/`).
- **Validation** — Every field: type, required/optional, ≥1 constraint.

## 4. Data Model Design

Per entity:

**Fields:** | Field | Type | Constraints | Default | Purpose |
**Relationships:** `Order belongs_to User` via FK — cascade behavior
**Indexes:** | Index | Type | Columns | Justification (by query pattern) |

Rules:
- **Migrations** — Additive (safe) vs breaking (needs coordination + rollback plan)
- **Soft vs hard delete** — Decide per entity with rationale
- **Seed data** — Reference data, lookup tables, fixtures
- **Entity summary** — One paragraph on how entities relate

## 5. System Architecture / Flow

Per major operation, write component-level sequence:

```
1. Client sends POST /api/orders
2. Auth middleware: validate JWT
3. Validation: check request body
4. Service: business logic
5. Database: BEGIN → INSERT → COMMIT
6. Event: OrderCreated → notification service
7. Response: 201 with order object
```

Also document:
- **Error paths** — What happens when step N fails? (rollback, status code, error code)
- **Transaction boundaries** — Which steps are transactional? Isolation level?
- **External deps** — Each service called, timeout, retry count, fallback

## 6. Error Handling Taxonomy

| Category | Status | Code Format | Log | Retry |
|---|---|---|---|---|
| Validation | 400 | `VALIDATION_{FIELD}` | warn | No |
| Auth | 401 | `AUTH_REQUIRED` | warn | No |
| Forbidden | 403 | `FORBIDDEN_{RESOURCE}` | warn | No |
| Not found | 404 | `{RESOURCE}_NOT_FOUND` | info | No |
| Conflict | 409 | `{RESOURCE}_{CONFLICT}` | warn | No |
| Business rule | 422 | `{RULE}_VIOLATED` | warn | No |
| System | 500 | `INTERNAL_ERROR` | error | No |
| External | 502/503 | `{SERVICE}_UNAVAILABLE` | error | Yes |

Error envelope must match existing project pattern. Retry: exponential backoff (1s, 2s, 4s) + jitter, max 3, circuit breaker at 5 failures/60s.

## 7. Security Considerations

- **Auth flow** — Token issuance/refresh, storage (httpOnly cookie/memory), expiry strategy
- **Input validation** — Where (API/service/DB), what each layer enforces, injection prevention
- **Data protection** — Fields needing encryption at rest, TLS, retention policy
- **Audit logging** — Which ops logged, format (`{ actor, action, resource, id, timestamp }`), retention
- **Rate limiting** — Per-endpoint + global limits, response headers
- **CORS** — Allowed origins, methods, headers, credentials

## 8. Performance Considerations

- **Caching** — What/where/TTL/invalidation trigger table
- **Query optimization** — N+1 prevention (eager loading), pagination for unbounded queries, indexes by query pattern
- **Payload/connection** — Size limits, pool size, timeouts
- **Async ops** — What to queue (email, webhooks, reports), queue tech, retry/dead-letter policy

## 9. Traceability

Every element uses `T-R{n}` tracing to SPEC.md:
- API: `T-R1: POST /api/orders` → R1
- Data: `T-R2: orders table` → R2
- Multiple: `T-R1a`, `T-R1b` for multiple elements per requirement

**Matrix:**
| Requirement | Technical Element(s) | Type |
|---|---|---|
| R{n} | T-R{n}: [element] | [type] |

If any R{n} has no T-R{n}, the design is incomplete.

## 10. TECHNICAL.md Output Template

```markdown
# Technical Design: [Feature Name]
**Last revised:** [date] — [summary if revised]

## Existing System Patterns
## Architecture Decision Records
### ADR-1: [Title]
## API Contracts
### T-R{n}: [Endpoint]
## Data Model
### T-R{n}: [Entity]
## System Architecture
### [Operation] Flow
## Error Handling
## Security
## Performance
## Traceability Matrix
```

## 11. Validation Checklist

- [ ] Every R{n} has ≥1 T-R{n} element; traceability matrix complete
- [ ] All API endpoints have complete request/response schemas with types + constraints
- [ ] All data models have fields, types, constraints, relationships, indexes
- [ ] ADRs for every non-trivial decision
- [ ] Error handling covers all failure modes with status + error codes
- [ ] Security addresses auth, validation, data protection
- [ ] Performance addresses caching + query optimization
- [ ] System flows include error propagation paths
- [ ] Existing patterns referenced by file path
- [ ] Migrations distinguish additive vs breaking with rollback
