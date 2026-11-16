# Recovery State — DomiBox Jira/Delivery Sync (DBX)

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.2 | 2026-11-16 | omp-orchestrator/recovery | `docs/08-delivery/jira-sync-map.json`<br>`docs/08-delivery/epic-catalogue.md`<br>`docs/08-delivery/bootstrap-status-report.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

## 1. Scope & Constraints (evidenced)
- Recovery performed from local workspace + Atlassian MCP reads only. No Jira items deleted/rewritten except none; no DNS/VPS/deploy changes; no secrets committed.
- Jira project: **DBX** (cloudId `f68721b3-e3c7-4a13-aaf9-527700a11dfc`, site `fikrichaerul.atlassian.net`).
- Correct search tool: `mcp__atlassian_searchjiraissuesusingjql` (note: earlier typo `mcp__atlassian_searchjirissuesusingjql` is invalid).

## 2. Jira Read Evidence (2026-11-15)

### 2.1 Project search (linkage fields)
- Query: `project = DBX ORDER BY key ASC`, `maxResults=50`, `fields=[summary,issuetype,status,parent,labels,priority,created,updated]`.
- Result: **28 issues**, `isLast=true`.
- **Parent/linkage:** every returned issue has `parent: null` (no epic-link/parent evidenced in search payload). Stories DBX-16..DBX-28 are type **Story** but no parent Epic evidenced.

| Key | ID | Type | Summary | Status | Priority | Labels | Parent evidenced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DBX-1 | 10186 | Epic | EPIC-01 — Domain & DNS Management (DomiBox) | To Do | High | domibox,epic | null |
| DBX-2 | 10187 | Task | SPIKE-01 — Probe Jira parent/Epic link registration (DomiBox) | To Do | High | infrastructure,spike | null |
| DBX-3 | 10188 | Epic | EPIC-02 — Mailbox Lifecycle Engine (DomiBox) | To Do | High | domibox,epic | null |
| DBX-4 | 10189 | Epic | EPIC-03 — Inbound Mail Pipeline (DomiBox) | To Do | High | domibox,epic | null |
| DBX-5 | 10190 | Epic | EPIC-04 — OTP & Link Extraction (DomiBox) | To Do | High | domibox,epic | null |
| DBX-6 | 10191 | Epic | EPIC-05 — Web Dashboard Application (DomiBox) | To Do | High | domibox,epic | null |
| DBX-7 | 10192 | Epic | EPIC-06 — Telegram Bot Channel (DomiBox) | To Do | High | domibox,epic | null |
| DBX-8 | 10193 | Epic | EPIC-07 — Security & HTML Sanitization (DomiBox) | To Do | High | domibox,epic | null |
| DBX-9 | 10194 | Epic | EPIC-08 — Background Jobs & Auto-Purge (DomiBox) | To Do | High | domibox,epic | null |
| DBX-10 | 10195 | Epic | EPIC-09 — Observability & Audit Trail (DomiBox) | To Do | Medium | domibox,epic | null |
| DBX-11 | 10196 | Epic | EPIC-10 — Docker & VPS Deployment (DomiBox) | To Do | High | domibox,epic | null |
| DBX-12 | 10197 | Epic | EPIC-11 — Automated Testing Suite (DomiBox) | To Do | Medium | domibox,epic | null |
| DBX-13 | 10198 | Epic | EPIC-12 — Technical Spikes & Feasibility (DomiBox) | To Do | High | domibox,epic | null |
| DBX-14 | 10199 | Epic | EPIC-13 — Documentation & Governance (DomiBox) | To Do | High | domibox,epic | null |
| DBX-15 | 10200 | Epic | EPIC-14 — Release & Cutover Management (DomiBox) | To Do | Medium | domibox,epic | null |
| DBX-16 | 10201 | Story | US-004 — Penerimaan Email Inbound & Penyimpanan Raw EML (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-17 | 10202 | Story | US-005 — Ekstraksi OTP & Tautan Aktivasi (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-18 | 10203 | Story | US-006 — Dashboard Web Inbox Viewer (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-19 | 10204 | Story | US-007 — Notifikasi Telegram Instan & Salin OTP (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-20 | 10205 | Story | US-008 — Sanitasi HTML Email & Isolasi Iframe (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-21 | 10206 | Story | US-009 — Auto-Purge & Cleanup Job Terjadwal (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-22 | 10207 | Story | US-010 — Observability, Logging & Audit Trail (DomiBox) | To Do | Medium | domibox,mvp,story | null |
| DBX-23 | 10208 | Story | US-011 — Docker Compose & Reverse Proxy TLS (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-24 | 10209 | Story | US-012 — Test Suite Unit/Integrasi/E2E (DomiBox) | To Do | Medium | domibox,mvp,story | null |
| DBX-25 | 10210 | Story | US-013 — Validasi Port 25 Inbound Tencent (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-26 | 10211 | Story | US-014 — Benchmark RAM Stalwart + PostgreSQL (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-27 | 10212 | Story | US-015 — Dokumentasi & Governance Baseline (DomiBox) | To Do | High | domibox,mvp,story | null |
| DBX-28 | 10213 | Story | US-016 — Checklist Kesiapan Rilis MVP (DomiBox) | To Do | Medium | domibox,mvp,story | null |

### 2.2 Individual issue reads
- `getJiraIssue(DBX-2)`: Task, To Do, High, labels `[infrastructure, spike]`, summary probe epic-link registration; no parent field evidenced in observed payload.
- `getJiraIssue(DBX-16..DBX-28)`: Stories as above; fields observed in compact responses: summary/status/assignee/priority/updated/labels (and id/key). **No parent and no description content surfaced in observed responses** despite field requests in some calls; linkage remains **NOT VERIFIED**.

### 2.3 Issue creation & parent linkage verification (2026-11-16)
- **DBX-29 created**: Story US-017 (canonical ID supersedes legacy catalogue US-001), parent DBX-3 (EPIC-02), status To Do, labels [domibox,mvp,story], SP not set. Description includes preconditions, 3 testable AC scenarios (temporary mailbox creation, TTL expiry, domain validation), proposed values marked as not confirmed.
- **DBX-30 created**: Story US-018 (canonical ID supersedes legacy catalogue US-003), parent DBX-3 (EPIC-02), status To Do, labels [domibox,mvp,story], SP not set. Description includes preconditions, 3 testable AC scenarios (temp→permanent conversion, quota persistence, alias state reconciliation), proposed quota marked as not confirmed.
- **DBX-31 created**: Story US-019 (canonical ID supersedes legacy catalogue US-004), parent DBX-1 (EPIC-01), status To Do, labels [domibox,mvp,story], SP not set. Represented as Story for user-visible onboarding/AC traceability (tasks may be split later). Description includes 3 AC scenarios (Cloudflare conflict detection, non-conflict domain validation, DNS failure handling).
- **DBX-2 parent linkage verified**: Task (probe spike), parent DBX-13 (EPIC-12), status To Do, labels [infrastructure,spike]. Linkage applied via editJiraIssue and confirmed via getJiraIssue readback.
- **DBX-16..DBX-28 parent linkage verified**: All 13 stories confirmed parented to correct Epics via getJiraIssue (2026-11-16): DBX-16→DBX-4(EPIC-03), DBX-17→DBX-5(EPIC-04), DBX-18→DBX-6(EPIC-05), DBX-19→DBX-7(EPIC-06), DBX-20→DBX-8(EPIC-07), DBX-21→DBX-9(EPIC-08), DBX-22→DBX-10(EPIC-09), DBX-23→DBX-11(EPIC-10), DBX-24→DBX-12(EPIC-11), DBX-25→DBX-13(EPIC-12), DBX-26→DBX-13(EPIC-12), DBX-27→DBX-14(EPIC-13), DBX-28→DBX-15(EPIC-14).
- **No duplicates**: JQL search `project = DBX` returns 31 issues total (DBX-1..DBX-31), all unique keys, no duplicate summaries.

## 3. Local Catalogue vs Jira Reconciliation

### 3.1 Epic catalogue (`docs/08-delivery/epic-catalogue.md`)
- Defines EPIC-01..EPIC-14 and “Katalog User Story MVP Pokok” **US-001..US-006**:
  - US-001: Pembuatan Mailbox Sementara Cepat
  - US-002: Ekstraksi Kode OTP Otomatis
  - US-003: Konversi Mailbox Sementara ke Permanen
  - US-004: Penanganan Konflik Cloudflare Email Routing
  - US-005: Pembersihan Otomatis Mailbox Kedaluwarsa (Auto-Purge)
  - US-006: Notifikasi & Ekstraksi OTP Instan via Telegram Bot

### 3.2 Jira story numbering/content collision (critical)
- Jira already contains stories labeled **US-004..US-016** as DBX-16..DBX-28 with **different content** than catalogue US-004..US-006:
  - DBX-16 / Jira “US-004” = Penerimaan Email Inbound & Penyimpanan Raw EML (≠ catalogue US-004 Cloudflare conflict handling)
  - DBX-17 / Jira “US-005” = Ekstraksi OTP & Tautan Aktivasi (**semantic overlap/duplicate intent** with catalogue US-002)
  - DBX-18 / Jira “US-006” = Dashboard Web Inbox Viewer (≠ catalogue US-006 Telegram notif)
  - DBX-19 / Jira “US-007” = Notifikasi Telegram Instan & Salin OTP (**semantic overlap** with catalogue US-006)
  - DBX-20 / Jira “US-008” = Sanitasi HTML Email & Isolasi Iframe
  - DBX-21 / Jira “US-009” = Auto-Purge & Cleanup Job Terjadwal (**semantic overlap** with catalogue US-005)
  - DBX-22..DBX-28 = US-010..US-016 (observability, docker/TLS, tests, port25 spike, RAM benchmark, docs/governance, release checklist) — no direct catalogue US-001..006 counterpart but occupy extended numbering.

### 3.3 Reconciliation decision (this recovery)
- **Canonical ID mapping resolved (2026-11-16):** Legacy catalogue US-001..US-006 superseded by canonical IDs US-017..US-019 and existing Jira stories. Mapping documented in `docs/08-delivery/epic-catalogue.md` section 2 (LEGACY NUMBERING SUPERSEDED table).
  - US-001 → US-017 (DBX-29, created 2026-11-16, parent DBX-3/EPIC-02)
  - US-002 → US-005 (DBX-17, existing, parent DBX-5/EPIC-04)
  - US-003 → US-018 (DBX-30, created 2026-11-16, parent DBX-3/EPIC-02)
  - US-004 → US-019 (DBX-31, created 2026-11-16, parent DBX-1/EPIC-01)
  - US-005 → US-009 (DBX-21, existing, parent DBX-9/EPIC-08)
  - US-006 → US-007 (DBX-19, existing, parent DBX-7/EPIC-06)
- **Missing distinct stories created:** DBX-29 (US-017, temporary mailbox), DBX-30 (US-018, temp→permanent conversion), DBX-31 (US-019, Cloudflare conflict handling) — all verified present in Jira with correct parents, types, statuses, labels, and AC descriptions.
- **No duplicates:** All 31 Jira issues (DBX-1..DBX-31) unique; no conflicting local_id mappings.

## 4. Sync Map Update (evidenced)
- `docs/08-delivery/jira-sync-map.json` updated to include DBX-1..DBX-31 (31 entries) from search/get/creation evidence.
- **Decision 5 metadata restructuring (2026-11-16):** Each entry now includes four distinct verification flags instead of single `verified` field:
  - `issue_existence_verified`: true/false — confirms Jira issue exists with correct key/type/status
  - `parent_relationship_verified`: true/false — confirms epic linkage via getJiraIssue parent field
  - `description_ac_verified`: true/false — confirms description contains testable AC (reviewed/updated 2026-11-16 for DBX-16..DBX-31)
  - `requirement_mapping_verified`: true/false — confirms canonical ID mapping (US-017..US-019 for new stories; US-004..US-016 for existing)
- DBX-2 parent linkage verified (DBX-13/EPIC-12) 2026-11-16.
- DBX-3..DBX-15 epics verified (existence/type/summary/status/labels 2026-11-15; epics have no parent by design).
- DBX-16..DBX-28 stories verified (parent linkage, description/AC content, SP estimates 2026-11-16).
- DBX-29..DBX-31 stories created and verified (parent linkage, description/AC content 2026-11-16; SP not set).

## 5. Blockers / Gaps (open)

| ID | Status | Detail | Resolution / Residual Gap |
| --- | --- | --- | --- |
| BLK-REC-001 | **RESOLVED** | Epic linkage/parent for DBX-2 and all stories DBX-16..DBX-31 not evidenced in 2026-11-15 search. | **Resolved 2026-11-16:** DBX-2 parent DBX-13 (EPIC-12) verified via editJiraIssue + getJiraIssue readback. DBX-16..DBX-28 parent linkages verified via getJiraIssue (all 13 stories confirmed parented to correct Epics). DBX-29..DBX-31 created with correct parents (DBX-3, DBX-3, DBX-1). No residual gap. |
| BLK-REC-002 | **RESOLVED** | Catalogue US-001..US-006 vs Jira US-004..US-016 numbering/content collision and semantic overlaps. | **Resolved 2026-11-16:** Canonical ID mapping documented in `docs/08-delivery/epic-catalogue.md` section 2 (LEGACY NUMBERING SUPERSEDED table). Legacy US-001..US-006 mapped to US-017, US-005, US-018, US-019, US-009, US-007 respectively. No residual gap. |
| BLK-REC-003 | **RESOLVED** | Catalogue items not represented as distinct verified Jira stories: US-001 (create temp mailbox), US-003 (convert temp→permanent), US-004-catalogue (Cloudflare Email Routing conflict handling). | **Resolved 2026-11-16:** DBX-29 (US-017, temp mailbox), DBX-30 (US-018, temp→permanent), DBX-31 (US-019, Cloudflare conflict) created and verified with correct parents, types, statuses, labels, and AC descriptions. No residual gap. |
| BLK-REC-004 | **PARTIALLY RESOLVED** | Story descriptions/Gherkin AC and custom fields (story points, etc.) not fully evidenced for DBX-16..DBX-28 in observed MCP responses. | **Updated 2026-11-16:** DBX-16..DBX-28 descriptions/AC reviewed and updated (evidenced in sync map notes). DBX-29..DBX-31 created with testable AC descriptions. Story points verified for DBX-16..DBX-28; DBX-29..DBX-31 SP not set. **Residual gap:** AC not executed/tested (only written); custom fields beyond SP/labels not comprehensively audited (e.g. start date, sprint, component). |
| BLK-REC-005 | **OPEN** | Local git working tree has unrelated modified file `WATCHDOG.yml` (not staged/committed by recovery). | **Unchanged:** Explicitly excluded from all recovery commits. Owner to review/commit or revert separately. |

## 6. Git / Delivery State (evidenced)
- Repo: inside work tree, branch `docs/project-bootstrap`, remote `origin https://github.com/lostsky1403/domibox.git`.
- Prior commits include `21cbf8d docs(jira-sync-map): add 13 verified Epics DBX-3..DBX-15`, `460d995`, `1151668`, `0236bac`, `b54f06d`.
- **2026-11-16 recovery commits:** This recovery run adds commits for `docs/08-delivery/recovery-state.md`, `docs/08-delivery/jira-sync-map.json`, and `docs/08-delivery/epic-catalogue.md` to document DBX-29/30/31 creation, parent linkage verification, and canonical ID mapping resolution.

## 7. Next Actions (recommended)
1. ~~Resolve BLK-REC-002: choose canonical story set and renumber catalogue or re-label mappings so each Jira issue has one unambiguous local_id.~~ **COMPLETED 2026-11-16** — canonical mapping documented in `docs/08-delivery/epic-catalogue.md` section 2.
2. ~~Resolve BLK-REC-001: discover/apply correct next-gen epic linkage field, link all stories/tasks to epics; re-read and verify.~~ **COMPLETED 2026-11-16** — all parent linkages verified (DBX-2→DBX-13, DBX-16..DBX-28→correct Epics, DBX-29..DBX-31→correct Epics).
3. ~~After decisions, create only truly missing non-overlapping stories (minimal, shortened summaries, no unverified story-points), readback-verify, update sync map.~~ **COMPLETED 2026-11-16** — DBX-29, DBX-30, DBX-31 created with canonical IDs US-017, US-018, US-019; all verified present in Jira with correct parents, types, statuses, labels, and AC descriptions.
4. ~~Verify/fetch full descriptions & AC for DBX-16..DBX-28; align with traceability matrix and DoD.~~ **COMPLETED 2026-11-16** — descriptions/AC reviewed and updated for DBX-16..DBX-28; DBX-29..DBX-31 created with testable AC. Story points verified for DBX-16..DBX-28; DBX-29..DBX-31 SP not set.
5. Keep `WATCHDOG.yml` out of recovery commits unless explicitly intended. **OPEN** — unchanged.
6. **NEW (2026-11-16):** Execute AC test cases for DBX-16..DBX-31 (currently only written, not executed).
7. **NEW (2026-11-16):** Audit custom fields beyond SP/labels (start date, sprint, component) for completeness.
