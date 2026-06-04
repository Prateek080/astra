# Technical Design: {{FEATURE_NAME}}

**Generated:** {{TIMESTAMP}}
**Spec:** REQUIREMENTS.md
**Design:** DESIGN_SPECS.md
**Plan:** PLAN.md
**Pipeline ID:** {{PIPELINE_ID}}

---

## Architecture Decision Records

### ADR-1: {{DECISION_TITLE}}
- **Status:** accepted
- **Context:** {{CONTEXT}}
- **Decision:** {{DECISION}}
- **Consequences:** {{CONSEQUENCES}}

---

## API Contracts

### T-R1: {{ENDPOINT_NAME}}
- **Requirement:** R1 — {{REQUIREMENT_TITLE}}

**Endpoint:** `{{METHOD}} {{PATH}}`

**Request:**
```json
{
  "{{field}}": "{{type}}"
}
```

**Response (success):**
```json
{
  "data": {},
  "meta": {}
}
```

**Response (error):**
```json
{
  "error": {
    "code": "{{ERROR_CODE}}",
    "message": "{{ERROR_MESSAGE}}"
  }
}
```

**Auth:** {{AUTH_REQUIREMENT}}
**Rate limit:** {{RATE_LIMIT}}

---

## Data Models

### {{MODEL_NAME}}
| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| id | uuid | PRIMARY KEY, NOT NULL | Auto-generated |
| {{field}} | {{type}} | {{constraints}} | {{notes}} |
| created_at | timestamp | NOT NULL, DEFAULT now() | |
| updated_at | timestamp | NOT NULL | Auto-updated |

### Indexes
- `idx_{{table}}_{{field}}` on `{{field}}`

### Migrations
- `{{MIGRATION_FILE}}` — {{DESCRIPTION}}

---

## Error Handling

### Error Taxonomy
| Code | HTTP | When | Response |
|------|------|------|----------|
| {{ERROR_CODE}} | {{STATUS}} | {{CONDITION}} | {{MESSAGE}} |

---

## Traceability Matrix

| Requirement | Technical Spec | API | Data Model |
|------------|---------------|-----|------------|
| R1 | T-R1 | {{METHOD}} {{PATH}} | {{MODEL}} |

### UI-only Requirements
_Requirements handled by designer agent (no backend component needed):_
- _None yet._

---

## Notes

- Every backend R{n} must have >= 1 T-R{n}.
- API endpoints need request + response schemas.
- Data models need field types and constraints (NOT NULL, UNIQUE, FK).
- Error codes follow SCREAMING_SNAKE_CASE taxonomy.
- No route conflicts with existing PRODUCT.md routes.
