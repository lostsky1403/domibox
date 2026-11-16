# Phase 1 PoC Execution Plan — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.2 | 2026-11-16 | omp-orchestrator/DeliveryDocs | bootstrap-status-report.md, epic-catalogue.md, recovery-state.md, jira-sync-map.json, ADR-001..ADR-012, traceability-matrix.md |

> No PoC step executed yet; all stories To Do; no benchmark/infra evidence.

## 1. Objectives
Validate three feasibility gates blocking implementation: (1) inbound mail reachability on port 25 + Stalwart SMTP acceptance (DBX-25); (2) resource envelope Stalwart+PostgreSQL within VPS RAM/CPU (DBX-26); (3) lifecycle correctness create/expiry/purge/permanent-conversion (DBX-21/29/30/31). Secondary: JMAP read/write, Cloudflare DNS/MX prereqs, rollback/cleanup, single pass/fail verdict with evidence. Out of scope: dashboard, Telegram, OTP extraction, sanitization, observability hardening, release cutover.

## 2. Environment & Prerequisites
Existing VPS `vps-tencent3b` (Ubuntu 24.04 LTS, 2 vCPU, 3.6 GiB RAM, public IP 43.153.206.84); Cloudflare zone + scoped API token; dedicated PoC domain; Docker Compose v2; Stalwart v1.1.0 (2026-11-09); PostgreSQL 15+; tools dig/swaks/curl/jq. Security prereqs: least-privilege token, default-deny firewall (open only 22/25/80/443), throwaway secrets, disposable data, STARTTLS via ACME, audit logging retained. **Upgrade caveat:** v1.1.0 adds passkey permissions to default roles; if upgrading from v1.0.x, set `STALWART_UPDATE_ROLE_PERMISSIONS=true` once during migration.

## 3. Port 25 Inbound Validation (DBX-25)
1. Verify existing VPS `vps-tencent3b` public IP + PTR record.
2. UFW default deny; allow 22/25; enable.
3. Confirm no upstream block: external `nc -vz <ip> 25`; document provider port-25 policy.
4. Deploy Stalwart Docker bound 0.0.0.0:25 with PoC domain.
5. Enable SMTP+submission, STARTTLS.
6. External send via swaks; verify 250 OK + message stored + raw EML retrievable.
7. Capture evidence: transcript, `ss -lntp`, logs, headers.
Pass: external delivery accepted/stored, port 25 reachable, STARTTLS negotiates. Fail: port blocked upstream, TLS/auth refusal, or not stored. Rollback: stop container, close 25, destroy VPS.

## 4. Cloudflare DNS/MX Prerequisites
1. Create zone; note zone ID + token.
2. Baseline: A mail.poc.example -> VPS IP; no MX initially.
3. Conflict check (DBX-31): dig MX; if any route*.mx.cloudflare.net -> CONFLICT_CLOUDFLARE_ROUTING, halt, show subdomain guidance (mail.poc.example); else proceed.
4. Add records: MX (priority 10), SPF TXT, DMARC TXT, DKIM TXT from Stalwart.
5. Verify propagation.
6. Document TTLs + record set.
Pass: MX resolves to Stalwart; SPF/DKIM/DMARC present; conflict path exercised. Fail: unreconcilable Cloudflare routing or propagation failure. Rollback: delete records/zone, revoke token.

## 5. Stalwart Trial Design
Docker Compose: Stalwart + PostgreSQL (metadata; blobs local volume for PoC). Admin via env; no public signup. Aliases via JMAP `x:Account/set` + `Mailbox/set` (Management API; standard `Mailbox/get` is read-only folder listing). Short TTL (60 min) to exercise expiry. TLS via ACME. Scenarios: (1) create alias via JMAP -> SMTP reachable; (2) inbound -> raw EML stored/parseable; (3) JMAP list -> count/headers; (4) delete alias -> 550; (5) 10 parallel alias creations -> no race/duplicate.

## 6. JMAP Checks
JMAP-01 auth 200+session; JMAP-02 Mailbox/get list; JMAP-03 create alias via `x:Account/set` (Management API) -> new id; JMAP-04 Email/get raw RFC822; JMAP-05 delete -> gone; JMAP-06 state change token; JMAP-07 invalid id -> 400/404 typed. Pass: all seven expected; state tokens usable.

## 7. Lifecycle Experiments (DBX-21/29/30/31)
7.1 DBX-29 (US-017 temp mailbox): create 60-min TTL; alias live via JMAP; inbound works; expires_at set; is_permanent=false. Pass: created+live+TTL+delivery.
7.2 DBX-21 (US-009 auto-purge): seed N expired mailboxes+messages; scheduler 60s; verify messages deleted DB+engine, mailbox PURGED, audit row, no table lock >2s, non-expired untouched. **Note:** scheduler requires DomiBox application code (not Stalwart alone). Pass: within one cycle, locks<2s, audit recorded.
7.3 DBX-30 (US-018 conversion): temp->permanent; expires_at=NULL, is_permanent=true, quota 100MB (proposed, owner confirm); alias persists; messages retained; no duplicate. **Note:** conversion requires DomiBox application code (not Stalwart alone). Pass: atomic conversion, quota applied, no orphan.
7.4 DBX-31 (US-019 conflict): domain with Cloudflare routing MX -> detection+hold+guidance; clean domain -> normal activation; DNS failure -> error path documented. Pass: conflict detected/guided, clean works, failure handled.

## 8. RAM/CPU Benchmark (DBX-26)
Method: baseline idle 5 min (RSS/CPU); load 10/50/100 msg/min 10 min each + concurrent JMAP reads; metrics docker stats, vmstat, pg_stat_activity, Stalwart metrics; record peak RSS, avg CPU, disk I/O, p50/p95 latency; vary VPS size if budget. Proposed pass (owner confirm): baseline idle RSS measured; under 100 msg/min RSS growth <50% of baseline (to be determined from measurements), CPU<80% sustained, p95<5s, no OOM; no crash in 30-min soak. Fail: OOM, CPU>90% sustained, p95>10s, crash. Output: benchmark report + min VPS tier recommendation.

## 9. Cleanup & Rollback
Per-run: `docker compose -p domibox-poc down -v` (explicit project name); delete DNS records/zone; revoke token; close firewall ports verify ufw; remove volumes/images; archive logs/evidence before destroy. **Resource ownership check:** all cleanup commands MUST verify resource ownership (e.g., `docker volume ls | grep domibox-poc`) before deletion. Triggers: any fail, security incident, cost overrun. Procedure: stop services, revert DNS, component-scoped rollback (NO VPS destruction), document incident+lessons.

## 10. Pass/Fail Criteria

### Phase-1A (Stalwart-only, PASS gates)
PASS only if ALL: (1) port 25 reachable + delivery accepted/stored (DBX-25); (2) Cloudflare DNS/MX configured + conflict-detection logic verified where possible (DBX-31: clean-zone positive path exercised; conflict path NOT TESTABLE until a simulated route*.mx.cloudflare.net record exists); (3) Stalwart scenarios 1-5 pass; (4) JMAP-01..07 pass; (5) lifecycle 7.1 (DBX-29 temp mailbox) + 7.4 (DBX-31 conflict detection) pass; (6) benchmark meets pass (DBX-26); (7) security prereqs satisfied, no secret leak; (8) evidence captured. Any FAIL -> Phase-1A FAILS; document in risk register; decide remediate or descope.

### Phase-1B (App-dependent, BLOCKED until DomiBox code exists)
Lifecycle 7.2 (DBX-21 auto-purge scheduler) and 7.3 (DBX-30 temp->permanent conversion) require DomiBox application code that does not exist yet. These tests are **BLOCKED** and cannot be executed during Phase-1 PoC. They will be deferred to Phase-2 integration testing after the application layer is implemented.

## 11. Dependencies & Risks
Cloud provider port-25 policy (verify before provisioning; fallback provider); Cloudflare routing conflict (subdomain strategy DBX-31); Stalwart version stability (pin version); PostgreSQL RAM (benchmark first); DNS propagation (low TTL + wait scripts); single-owner VPS no HA (acceptable PoC); unverified proposed values quota/TTL (owner confirmation gate). Jira: DBX-25, DBX-26, DBX-21, DBX-29, DBX-30, DBX-31, DBX-13, DBX-11.

## 12. Evidence & Reporting
Evidence under docs/08-delivery/poc-evidence/ (create during execution) or attached to Jira. Final report docs/08-delivery/phase1-poc-report.md after execution. This plan stays PROPOSED until execution; update Status to EXECUTED with results appended.


## 13. Stalwart Management API Reference (Added 2026-11-16)

**NOT VERIFIED — PoC must validate before reliance.**

The following claims about Stalwart v1.1.0 Management API are **unverified from official documentation**. The reference URL `https://stalw.art/docs/jmap/management` returns HTTP 404. PoC execution MUST validate these claims against actual server behavior.

**Claimed endpoints (UNVERIFIED):**
- `x:Account/set` — create/modify/delete mail accounts (requires admin auth)
- `x:Alias/set` — create/modify/delete aliases (requires admin auth)
- `Mailbox/set` — create/modify/delete mailbox folders (requires account auth)
- `Email/set` — create/modify/delete email messages (requires account auth)

**Claimed authentication (UNVERIFIED):**
- Management API: admin credentials via HTTP Basic Auth or Bearer token
- Standard JMAP: account credentials via Bearer token

**Claimed permissions (UNVERIFIED):**
- Admin can create/modify/delete any account or alias
- Account owner can modify/delete own mailboxes and messages
- No cross-account access without explicit delegation

**PoC validation steps:**
1. Deploy Stalwart v1.1.0 with default config
2. Attempt `POST /jmap` with `x:Account/set` method using admin credentials
3. Document actual endpoint names, auth methods, and permission model
4. Update this section with verified facts or mark as BLOCKED if endpoints do not exist

**Reference:** Stalwart v1.1.0 release notes (https://github.com/stalwartlabs/stalwart/releases/tag/v1.1.0); JMAP overview (https://stalw.art/docs/http/jmap); specific Management API reference URL not found (404).
