# Recovery State — DomiBox Jira/Delivery Sync (DBX)

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-15 | omp-orchestrator/recovery | `docs/08-delivery/jira-sync-map.json`<br>`docs/08-delivery/epic-catalogue.md`<br>`docs/08-delivery/bootstrap-status-report.md`<br>`docs/02-requirements/traceability/traceability-matrix.md` |

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
- `getJiraIssue(DBX-29)`: **404** `Issue "DBX-29" not found`. Catalogue/local assumption “US-001 → DBX-3” cannot be satisfied by DBX-29; treat as **MISSING / not present**.

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
- **No new Jira story issues created** in this recovery for catalogue US-001..US-006.
  - Creating catalogue US-001–US-006 now would risk **permanent duplicates** and conflicting local_id mappings (plan forbids deleting Jira items; advisories require reconciliation first).
  - Catalogue US-002 semantically overlaps DBX-17; catalogue US-005 overlaps DBX-21; catalogue US-006 overlaps DBX-19; catalogue US-001/US-003 overlap mailbox-lifecycle scope (Epic DBX-3/EPIC-02). Free/unmapped catalogue IDs must be treated as **gap/not-created**, not auto-created.
  - Catalogue US-004 (Cloudflare conflict handling) is **missing as distinct Jira story** but its numeric label is already occupied in Jira by DBX-16 (different content) — requires explicit renumbering/mapping decision.
- **Authoritative mapping unresolved:** `jira-sync-map.json` records Jira-grounded issue existence for DBX-1..DBX-28 with conflict notes; catalogue US-001..US-006 remain **unmapped/blocked** pending owner/PM decision on canonical story set and renumbering.

## 4. Sync Map Update (evidenced)
- `docs/08-delivery/jira-sync-map.json` updated to include DBX-1..DBX-28 (28 entries) from search/get evidence.
- DBX-2 kept **unverified** (probe linkage/parent not evidenced).
- DBX-3..DBX-15 epics **verified** (existence/type/summary/status/labels evidenced via search 2026-11-15).
- DBX-16..DBX-28 stories added as **verified Jira issues** but with `epic_reference: null`, `parent_evidenced: false`-equivalent notes, and catalogue-collision notes where applicable; **no fabricated epic links**.
- DBX-29 not added (404 / does not exist).

## 5. Blockers / Gaps (open)

| ID | Status | Detail | Needed |
| --- | --- | --- | --- |
| BLK-REC-001 | BLOCKED | Epic linkage/parent for DBX-2 and all stories DBX-16..DBX-28 not evidenced (`parent: null` in search; not surfaced in getJiraIssue). | Determine correct epic-link field/mechanism for DBX next-gen project; link stories/tasks to epics; re-read and verify. |
| BLK-REC-002 | BLOCKED | Catalogue US-001..US-006 vs Jira US-004..US-016 numbering/content collision and semantic overlaps (US-002↔DBX-17, US-005↔DBX-21, US-006↔DBX-19; US-001/US-003 mailbox-lifecycle overlap). | Owner decision: canonical story catalogue + renumbering/mapping (e.g. adopt Jira set, remap catalogue IDs, or create new non-colliding IDs) before any story creation. |
| BLK-REC-003 | OPEN | Catalogue items not represented as distinct verified Jira stories: US-001 (create temp mailbox), US-003 (convert temp→permanent), US-004-catalogue (Cloudflare Email Routing conflict handling) — **not created** this recovery to avoid duplicates. | Create/map after BLK-REC-002 resolved; readback-verify each. |
| BLK-REC-004 | NOT VERIFIED | Story descriptions/Gherkin AC and custom fields (story points, etc.) not fully evidenced for DBX-16..DBX-28 in observed MCP responses. | Fetch full issue content (`fields=description,...`) and verify against delivery spec. |
| BLK-REC-005 | OPEN | Local git working tree has unrelated modified file `WATCHDOG.yml` (not staged/committed by recovery). | Owner to review/commit or revert separately. |

## 6. Git / Delivery State (evidenced)
- Repo: inside work tree, branch `docs/project-bootstrap`, remote `origin https://github.com/lostsky1403/domibox.git`.
- Prior commits include `21cbf8d docs(jira-sync-map): add 13 verified Epics DBX-3..DBX-15`, `460d995`, `1151668`, `0236bac`, `b54f06d`.
- This recovery intends **one commit** for `docs/08-delivery/recovery-state.md` and `docs/08-delivery/jira-sync-map.json`, then push (subject to auth/network).

## 7. Next Actions (recommended)
1. Resolve BLK-REC-002: choose canonical story set and renumber catalogue or re-label mappings so each Jira issue has one unambiguous local_id.
2. Resolve BLK-REC-001: discover/apply correct next-gen epic linkage field, link all stories/tasks, verify parent.
3. After decisions, create only truly missing non-overlapping stories (minimal, shortened summaries, no unverified story-points), readback-verify, update sync map.
4. Verify/fetch full descriptions & AC for DBX-16..DBX-28; align with traceability matrix and DoD.
5. Keep `WATCHDOG.yml` out of recovery commits unless explicitly intended.
