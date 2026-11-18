# Revision and Approval Policy (DomiBox Docs)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance`  

## 1. Purpose
Define how documentation changes are proposed, reviewed, approved, versioned, and superseded.

## 2. Roles
| Role | Responsibilities |
| --- | --- |
| Owner | Maintains document accuracy, proposes revisions, updates metadata/version |
| Reviewer(s) | Validates correctness, completeness, traceability, and risks |
| Approver | Confirms baseline acceptance for scope (can be delegated by governance plan) |
| Orchestrator | Ensures cross-document consistency and audit/report updates |

## 3. Revision Workflow
1. **Draft/Propose:** Create or edit document with `Status: PROPOSED` and increment minor/doc version as needed.
2. **Review:** Reviewer(s) check standards compliance, evidence labels, ID/traceability correctness, and cross-doc impacts.
3. **Decision:** Approve, request changes, or defer (record significant decisions in decision log/ADR as applicable).
4. **Baseline:** Set `Status: APPROVED`, update date/version, and record approval metadata if available.
5. **Subsequent Changes:** New material changes require version bump and changelog/update note.

## 4. Versioning Guidance
- `0.x`: Draft/proposed iterations (bootstrap phase typical).
- `1.0`: First approved baseline for a document.
- Minor increments (`1.1`, `1.2`) for non-breaking clarifications/additions.
- Major increments (`2.0`) for substantial scope/decision changes or superseding restructures.

## 5. Status Transitions
| From | To | Condition | Required Actions |
| --- | --- | --- | --- |
| PROPOSED | APPROVED | Review complete and accepted | Update metadata, changelog/sign-off, align traceability |
| APPROVED | PROPOSED | Reopened for material revision | Increment version, note reason/change scope |
| APPROVED/PROPOSED | SUPERSEDED | Replaced by another artifact | Set status, add replacement link/reference, preserve history |
| APPROVED/PROPOSED | DEPRECATED | No longer applicable | Set status, state reason/date, retain for audit history |

## 6. Approval Evidence
- Preferred: explicit sign-off table/entry in the document and/or decision log reference.
- If approvals are pending/unavailable, keep `PROPOSED` and record open question/next step (no fabricated approvals).

## 7. Cross-Document Change Requirements
- Update `traceability-matrix.md` when requirement/test/delivery mappings change.
- Update `open-questions.md` and `decision-log.md` for unresolved issues or key decisions.
- Update impacted diagrams/specs when contracts or architecture decisions change.

## 8. Auditability Rules
- Do not rewrite historical meaning without trace; use changelog entries or supersession.
- Preserve prior templates/artifacts when policy requires (e.g., original PRD template).
