# Open Questions Register (DomiBox)

**Status:** `PROPOSED`  
**Version:** `0.1`  
**Date:** `2026-11-14`  
**Owner:** `Governance / Product / Architecture (shared)`  

## Purpose
Track unresolved questions that affect scope, requirements, architecture, delivery, security, or operations.

## Open Questions
| ID | Question | Category | Impacted Artifacts/IDs | Owner | Needed By | Priority | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | What are the verified source findings for Problem-Value Research? | Research/Evidence | `docs/09-research/problem-value-research.md`, BR/FR derivation | Product/Research | Before requirements baseline approval | High | Open | Placeholder created; session source not found |
| Q-002 | What are the verified source findings for Competitive-Comparative Research? | Research/Evidence | `docs/09-research/competitive-comparative-research.md`, positioning/requirements | Product/Research | Before requirements baseline approval | High | Open | Placeholder created; session source not found |
| Q-003 | What are the MVP boundaries between temporary and permanent mailbox capabilities? | Product Scope | PRD, BR/FR/NFR/SEC, epics/stories | Product | Before Phase 3/8 finalization | High | Open | Must be explicitly defined to avoid scope drift |
| Q-004 | What authentication/identity model is required for MVP (anonymous, account-based, hybrid)? | Architecture/Security | ADRs, FR/SEC/NFR, API design | Architecture/Security | Before architecture baseline | High | Open | Impacts data model and abuse controls |
| Q-005 | What is the authoritative Jira issue taxonomy/required fields in DBX for Epics/Stories/Tasks/Spikes? | Delivery Tooling | Jira sync, delivery docs | Delivery/Orchestrator | Phase 12 | Medium | Open | Probe during Jira integration; adapt idempotently |
| Q-006 | Is GitHub push/PR creation permitted with available credentials in this environment? | Repo/Process | Phase 11 outputs | Orchestrator/User | Phase 11 | Medium | Open | `gh` currently unauthenticated |

## Closure Rules
- When resolved, update `Status` to `Closed`, add resolution summary in Notes, and link decision/change references.
- If a question becomes a formal decision, add `DEC-*` entry and cross-reference.
