# Documentation Standards (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Orchestrator / Governance`  

## 1. Purpose
Define mandatory conventions for all documentation artifacts in this repository to ensure consistency, traceability, reviewability, and auditability.

## 2. Scope
Applies to all files under `docs/`, root governance files, and issue/PR templates that describe scope, requirements, architecture, delivery, operations, or compliance.

## 3. Document Metadata (Required)
Every normative markdown document MUST start with:
- **Status:** `PROPOSED | APPROVED | SUPERSEDED | DEPRECATED`
- **Version:** semantic-like doc version (e.g., `0.1`, `1.0`)
- **Date:** ISO-like date of last material update (`YYYY-MM-DD`)
- **Owner:** role/team/persona responsible for maintenance

Optional but recommended: `Reviewers`, `Related`, `Supersedes`.

## 4. Status Semantics
- `PROPOSED`: Drafted, not yet approved for baseline.
- `APPROVED`: Reviewed and accepted as baseline for its scope.
- `SUPERSEDED`: Replaced by a newer document/version (must reference replacement).
- `DEPRECATED`: No longer applicable; retained for history.

## 5. ID Schemes (Canonical)
Use stable, unique identifiers. Do not reuse retired IDs.

| Domain | Format | Example |
| --- | --- | --- |
| Business Requirement | `BR-###` | `BR-001` |
| Functional Requirement | `FR-###` | `FR-012` |
| Non-Functional Requirement | `NFR-###` | `NFR-004` |
| Security/Privacy Control | `SEC-###` | `SEC-007` |
| Architecture Decision Record | `ADR-###` | `ADR-003` |
| Test Case | `TC-###` | `TC-021` |
| Risk | `RISK-###` | `RISK-005` |
| Open Question | `Q-###` | `Q-010` |
| Decision Log Entry | `DEC-###` | `DEC-002` |

## 6. Traceability Rules
- Every `FR-*` MUST trace to ≥1 `BR-*` (or explicitly state rationale if foundational/platform requirement).
- Security/privacy-sensitive requirements MUST map to relevant `SEC-*` and/or `NFR-*`.
- Test artifacts (`TC-*`) MUST map to requirements and, where applicable, risks.
- Delivery artifacts (epics/stories/tasks) MUST reference requirement IDs in descriptions/acceptance criteria.
- `docs/02-requirements/traceability/traceability-matrix.md` is the canonical cross-reference index.

## 7. Writing & Evidence Rules
- **No invention:** Do not fabricate dates, metrics, approvals, external facts, or integration states.
- **Evidence tagging:** Mark key claims as `VERIFIED`, `ASSUMPTION`, or `PROPOSED` where ambiguity exists.
- **Citations:** Research and comparative claims should cite sources/links when available; if unavailable, state gap explicitly.
- **Clarity:** Prefer concise tables, explicit scope, and testable acceptance criteria.

## 8. Mermaid Diagram Standard
- Use Mermaid fenced blocks (```mermaid) for architecture/flow diagrams.
- Keep diagrams syntactically valid and readable (clear node labels, directional flow).
- Complex diagrams should include a short textual summary below the block.
- Do not claim diagram render verification unless actually validated.

## 9. File Naming & Placement
- Use kebab-case filenames (except established templates like `TEMPLATE_PRD.md`).
- Place artifacts in the designated domain folder (product, requirements, architecture, etc.).
- Governance-wide artifacts live in `docs/00-governance/`.

## 10. Change Control
- Material changes to `APPROVED` docs require version bump and decision/log update as applicable.
- Superseded docs must include pointer to replacement and date/status change.
- Cross-document impacts must be reflected in traceability and open questions/decisions.

## 11. Review Checklist (Minimum)
- Metadata present and accurate
- IDs unique and correctly formatted
- No invented facts/dates/approvals
- Traceability links updated
- Security/privacy and ops implications considered (where relevant)
- Diagrams/tables render logically and align with text
