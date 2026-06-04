# Implementation Plan: {{FEATURE_NAME}}

**Generated:** {{TIMESTAMP}}
**Mode:** {{MODE}}
**Spec:** REQUIREMENTS.md
**Design:** DESIGN_SPECS.md
**Pipeline ID:** {{PIPELINE_ID}}

---

## Phase 1: {{PHASE_TITLE}}

**Parallel:** no
**Requirements:** R1

### Tasks
- [ ] {{TASK_1}}
- [ ] {{TASK_2}}

### Files to create
- `{{FILE_PATH}}`

### Files to modify
- `{{FILE_PATH}}`

### Test gate
- [ ] {{TEST_COMMAND}} passes
- [ ] {{VERIFICATION_STEP}}

---

## Dependency Graph

```
Phase 1 → Phase 2 → Phase 3
```

---

## Notes

- Each phase must be independently verifiable and completable in < 50% context.
- Every R{n} from REQUIREMENTS.md must appear in at least one phase.
- Each phase needs a test gate with runnable verification commands.
- Mark independent phases with `Parallel: yes` for concurrent execution.
- Phases have 1-8 tasks (split oversized phases).
- Data/model phases come before UI phases.
