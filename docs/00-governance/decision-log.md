# Decision Log (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Orchestrator`  

## Purpose
Track key project/documentation decisions, rationale, alternatives, and impacts. This log complements ADRs (architecture-specific decisions).

## Decision Entries
| ID | Date | Decision | Context | Options Considered | Rationale | Impact | Status | Links |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEC-001 | 2026-11-14 | Use canonical ID schemes (BR/FR/NFR/SEC/ADR/TC/RISK/Q/DEC) across docs | Need consistent traceability for bootstrap artifacts and Jira mapping | Ad hoc IDs; per-document numbering; canonical cross-doc scheme | Canonical scheme improves traceability, auditability, and delivery mapping | All downstream docs must conform | APPROVED (session bootstrap) | `docs/00-governance/documentation-standards.md` |
| DEC-002 | 2026-11-14 | Preserve original PRD template and add improved version | Existing template lacks governance/traceability/security coverage | Replace in place; preserve and augment | Preserve history while enabling better future PRDs | Both templates coexist; improved one preferred | APPROVED (session bootstrap) | `docs/00-governance/prd-template-audit.md`, `docs/01-product/prd/TEMPLATE_PRD_IMPROVED.md` |
| DEC-003 | 2026-11-14 | Mark missing/problematic research sources explicitly instead of inventing content | Two required research source files not found in session search; two others required repair | Fabricate research; omit artifacts; create explicit placeholders with gaps | Preserves integrity and auditability | Downstream docs must record evidence gaps/assumptions | APPROVED (session bootstrap) | `docs/09-research/problem-value-research.md`, `docs/09-research/competitive-comparative-research.md` |
| DEC-004 | 2026-11-15 | Materialize canonical research outputs (F1-F6) while preserving source artifacts | Ensure all canonical research paths (mail-infrastructure-feasibility, ux-pattern-research, tech-stack-evaluation, security-controls-research) exist with verifiable F1-F6 evidence labels | Overwrite existing research files; create canonical aliases; reconcile and cross-link | Preserves historical research detail in suitability/benchmark while providing standardized canonical documents | Downstream architecture, requirements, and governance docs gain unambiguous canonical links | APPROVED (session bootstrap) | `docs/09-research/mail-infrastructure-feasibility.md`, `docs/09-research/ux-pattern-research.md`, `docs/09-research/tech-stack-evaluation.md`, `docs/09-research/security-controls-research.md` |

## Update Rules
- Append new decisions; do not rewrite history except factual corrections (note correction in a new row or revision note).
- Reference impacted docs/IDs.
- Superseded decisions must point to replacement decision.
