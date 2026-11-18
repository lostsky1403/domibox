# Phase 1 Readiness Review — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.2 | 2026-11-18 | OpenChamber/DeliveryDocs (live reconciliation) | `docs/08-delivery/bootstrap-status-report.md`<br>`docs/08-delivery/epic-catalogue.md`<br>`docs/08-delivery/recovery-state.md`<br>`docs/08-delivery/jira-sync-map.json`<br>`docs/08-delivery/phase1-preflight-report.md`<br>`docs/08-delivery/plans/phase1-poc-execution-plan.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

---

## Verdict: **READY FOR CONTROLLED POC — CONDITIONAL / APPROVAL-GATED**

Phase 1 (documentation bootstrap + Jira reconciliation) is materially complete and internally consistent. The 2026-11-18 live preflight (`docs/08-delivery/phase1-preflight-report.md`) **VERIFIED** that `vps-tencent3b` is up and provisioned with ample headroom (2 vCPU, 3.6 GiB RAM / 2.3 GiB available, 48 GB disk, Docker 29.9.3 + Compose v5.7.0, Caddy on 80/443, port 25 free on host). The prior `PARTIALLY READY` was caused by an OMP-environment SSH timeout, now resolved. Phase 1 PoC execution has still NOT started; all PoC stories remain `To Do`, and the infrastructure go/no-go depends on the approval gates in §9. VPS reachability does not close implementation stories.

---

## 1. Completeness

**Done (documentation layer):**

- Governance baseline: charter, standards, RACI, risk register, assumption log, open questions, communication plan, decision log, document control register, revision/approval policy, PRD template audit.
- Product core: vision, value proposition, MVP scope, personas, stakeholder map, UX principles, IA/interaction spec, prototype notes.
- Requirements: BRD, SRS, functional specs (7), NFR spec, security/privacy requirements, scope/change control, requirements assumptions register.
- Architecture: overview, capacity planning, 12 ADRs, 5 C4/deployment diagrams, domain onboarding flow, email flow sequence, expiration/deletion flow, lifecycle state machine, network port matrix, failure mode analysis, tech evaluation matrix.
- Technical: API spec + OpenAPI, data model, DB schema, deployment spec, error catalogue, mail flow spec, OTP extraction spec, Telegram bot spec.
- Security/privacy: threat model (in `docs/05-security/`); `docs/05-security-privacy/` is a README scaffold.
- Quality: test strategy (TC-001..TC-008 only `PROPOSED`).
- Operations: deployment architecture (README-level).
- Delivery: epic catalogue (14 epics), bootstrap status report, recovery state, Jira sync map (31 entries), this review, PoC execution plan.

**Incomplete / open:**

- `docs/05-security-privacy/` and `docs/10-release/` are README scaffolds only.
- `docs/08-delivery/milestones/` is empty.
- `docs/10-ux/` scaffold only.
- `docs/05-security/` vs `docs/05-security-privacy/` ownership unresolved (duplicate/overlap noted).
- `WATCHDOG.yml` has uncommitted local changes (excluded from all commits).
- No application code, no tests executed, no PoC evidence.

---

## 2. Traceability Coverage

- RTM (`docs/02-requirements/traceability/traceability-matrix.md`) reconciled; Jira placeholders `DBX-STORY-TBD-*` removed; 31 unique DBX issues recorded.
- OPS mapping canonical: FR-008/OPS-001..005 (auth, auto-purge/NFR-008, health, rate limit/SEC-009, audit/SEC-008). Note: OPS-001 (auth) and OPS-004 (rate limiting) have no story-level mapping/AC yet (story-level GAP; epic-level DBX-8/EPIC-07).
- Legacy `LOG-1 → OPS-002/OPS-005`; Mermaid coverage to NFR-001..012 & SEC-001..012.
- MBX permanent mapping: FR-003/MBX-003 (permanent conversion), MBX-002 (TTL extension); BRD downstream SEC-001..012.
- ADR status and TC-001..TC-008 remain `Pending`/`PROPOSED` — traceability links exist but verification not executed.
- **Gap:** AC execution evidence absent; TCs not run; custom fields beyond SP/labels not audited.

---

## 3. Remaining ADR Decisions

All 12 ADRs (`ADR-001`..`ADR-012`) are in `PROPOSED` / `NEEDS OWNER APPROVAL` state. No ADR has been accepted. Key decisions still pending owner sign-off:

- ADR-001.. (identity/auth model) — ties to open question Q-004.
- ADRs covering Stalwart vs alternatives, PostgreSQL, Cloudflare DNS strategy, TTL defaults, quota values (100 MB proposed), Telegram bot hosting, security sanitization approach.
- Proposed values (quota 100 MB, TTL 60 min, scheduler 60s) are marked as not confirmed in Jira AC descriptions.

**Action:** Owner review and accept/reject each ADR before implementation; record decisions in `docs/00-governance/decision-log.md`.

---

## 4. Critical / High Security + Architecture Findings

**Security:**

- `docs/05-security/threat-model.md` exists; `docs/05-security-privacy/` is scaffold only → security/privacy artefacts split and incomplete.
- HTML sanitization (DOMPurify + iframe isolation) specified but not implemented/tested (DBX-20).
- WebAuthn/TOTP, rate limiting (SEC-009) specified; not implemented.
- Port 25 exposure risk: provider policy and firewall config unverified (DBX-25).
- Secrets management for PoC/production not yet defined; PoC must use throwaway values.
- No security review executed; no pentest baseline.

**Architecture:**

- Capacity planning exists but RAM envelope unverified (DBX-26).
- Single-VPS, no HA; acceptable for PoC/MVP but a risk for production.
- Duplicate/overlap: `docs/05-security/` vs `docs/05-security-privacy/` ownership unresolved.
- Cloudflare Email Routing conflict path (DBX-31) specified but unexecuted.

**Risk register:** `docs/00-governance/risk-register.md` exists; PoC-specific risks captured in `phase1-poc-execution-plan.md` §11.

---

## 5. Jira Backlog Readiness

- **31 issues** (DBX-1..DBX-31): 14 Epics, 16 Stories, 1 Task (DBX-2 spike). All `To Do`, priority High/Medium.
- Parent linkage verified for all stories/tasks; 14 epics have no parent by design.
- `description_ac_verified` true for 16 stories (DBX-16..DBX-31); epics + DBX-2 marked `not_reviewed` (summary only).
- Story points verified for DBX-16..DBX-31; epics/DBX-2 not estimated.
- **Gaps:** AC written but not executed; custom fields beyond SP/labels unaudited; no sprint assignment; no start dates.
- **Missing stories:** OPS-001 (auth) and OPS-004 (rate limit) story gaps noted in recovery state; verify whether covered by existing stories or need new issues.

---

## 6. Phase 1 PoC Prerequisites

All items in `phase1-poc-execution-plan.md` are unexecuted:

- Port 25 inbound validation (DBX-25).
- Cloudflare DNS/MX prerequisites + conflict handling (DBX-31).
- Stalwart trial design + JMAP checks.
- Lifecycle experiments (DBX-21, DBX-29, DBX-30, DBX-31).
- RAM/CPU benchmark (DBX-26).
- Security prerequisites (§2 of plan).
- Evidence capture and PoC report.

**Blockers (updated 2026-11-18):** VPS provisioning is `VERIFIED` complete and is no longer a blocker. Remaining gates: inbound TCP/25 approval (Tencent SG + UFW — externally FILTERED, no listener), Cloudflare DNS record additions (approval-gated), Stalwart version pin decision (v1.1.0 plan vs v1.0.3 ADR-002), Management API validation (`NOT VERIFIED`), and owner approval of ADRs/proposed values. Phase 1B remains `BLOCKED` pending DomiBox application code.

---

## 7. Commit SHA / PR Verification

- **Branch:** `docs/project-bootstrap` (tracking `origin/docs/project-bootstrap`).
- **HEAD (pre-this-commit):** `1d17478` (`fix(rtm): remove fabricated SP for DBX-29/30/31, fix OTP spacing typos`).
- **Remote:** `https://github.com/lostsky1403/domibox.git`.
- **PR #1:** open, draft, head `docs/project-bootstrap` (to be verified after push).
- **Uncommitted changes:** `WATCHDOG.yml` modified (excluded; owner decision pending).
- This review commit will be pushed to `docs/project-bootstrap`; PR #1 draft expected to update automatically.

---

## 8. Owner Approval Decisions Required

1. Accept/reject each ADR-001..ADR-012 (record in decision log).
2. Confirm proposed values: mailbox TTL 60 min, permanent quota 100 MB, scheduler interval 60s, lock threshold 2s.
3. Confirm PoC VPS provider and budget tier.
4. Confirm dedicated PoC domain and Cloudflare zone.
5. Decide canonical ownership of `docs/05-security/` vs `docs/05-security-privacy/`.
6. Decide handling of uncommitted `WATCHDOG.yml` changes.
7. Confirm Jira custom-field audit scope (start date, sprint, component).
8. Confirm whether OPS-001/OPS-004 need new stories or are covered.

---

## 9. Recommended Next Action

**Immediate (owner):** Review and approve ADRs + proposed values; provision PoC VPS/domain/Cloudflare token.

**Immediate (agent, after approval):** Execute Phase 1 PoC per `phase1-poc-execution-plan.md`; capture evidence; author `phase1-poc-report.md` with pass/fail verdict.

**Then:** Close TC-001..TC-008 with execution evidence; run security review; complete scaffold artefacts (`docs/05-security-privacy/`, `docs/10-release/`, milestones); prepare implementation kickoff.

---

## Exact Blockers (must close before implementation kickoff)

1. ADR-001..ADR-012 all `PROPOSED` — no accepted architecture decisions.
2. TC-001..TC-008 only `PROPOSED` in test-strategy; no test cases executed.
3. AC for DBX-16..DBX-31 written but not executed.
4. Phase 1 PoC not run (DBX-25, DBX-26, DBX-21/29/30/31 all `To Do`).
5. `docs/05-security-privacy/` and `docs/10-release/` are README scaffolds.
6. `docs/08-delivery/milestones/` empty.
7. OPS-001/OPS-004 story coverage unverified.
8. Jira custom fields beyond SP/labels unaudited.
9. `WATCHDOG.yml` uncommitted changes (owner decision pending) — working tree was clean at the 2026-11-18 preflight.
10. No owner approval recorded for any ADR or proposed value.
11. **(NEW, 2026-11-18) Inbound TCP/25 not authorized** — Tencent SG rule + UFW allow required; external probe FILTERED; no active listener. `BLOCKED`.
12. **(NEW, 2026-11-18) Cloudflare DNS records not added** — A/MX/SPF/DMARC/DKIM approval-gated. `REQUIRES APPROVAL`.
13. **(NEW, 2026-11-18) Stalwart version pin conflict** — PoC plan v1.1.0 vs ADR-002/architecture v1.0.3. `REQUIRES APPROVAL`.
14. **(NEW, 2026-11-18) Stalwart Management API endpoints/auth unverified** (plan §13). `NOT VERIFIED`.

**No longer a blocker (VERIFIED 2026-11-18):** VPS provisioning / SSH reachability — prior OMP SSH timeout was environmental; OpenChamber local terminal reaches `vps-tencent3b` with `BatchMode=yes`.
