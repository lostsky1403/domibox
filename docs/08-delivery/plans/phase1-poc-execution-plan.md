# Phase 1 PoC Execution Plan — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.3 | 2026-11-18 | OpenChamber/DeliveryDocs (live reconciliation) | bootstrap-status-report.md, epic-catalogue.md, recovery-state.md, jira-sync-map.json, phase1-preflight-report.md, ADR-001..ADR-012, traceability-matrix.md |

> No PoC step executed yet; all stories To Do; no benchmark/infra evidence. A **read-only VPS preflight was completed 2026-11-18** (`docs/08-delivery/phase1-preflight-report.md`): infra readiness `VERIFIED`, no deployment performed.

## 1. Objectives
Validate three feasibility gates blocking implementation: (1) inbound mail reachability on port 25 + Stalwart SMTP acceptance (DBX-25); (2) resource envelope Stalwart+PostgreSQL within VPS RAM/CPU (DBX-26); (3) lifecycle correctness create/expiry/purge/permanent-conversion (DBX-21/29/30/31). Secondary: JMAP read/write, Cloudflare DNS/MX prereqs, rollback/cleanup, single pass/fail verdict with evidence. Out of scope: dashboard, Telegram, OTP extraction, sanitization, observability hardening, release cutover.

## 2. Environment & Prerequisites
Existing VPS `vps-tencent3b` (Ubuntu 24.04.5 LTS, kernel 6.8.0-138-generic, 2 vCPU AMD EPYC 7K62, 3.6 GiB RAM / 2.3 GiB available, 1.9 GiB swap, 59 GB disk / 48 GB free, public IP 43.153.206.84) — **all VERIFIED 2026-11-18T14:23:06Z**. Docker 29.9.3 + Compose v5.7.0 `VERIFIED`; one unrelated loopback-only `rustfs` container; no Docker volumes. Caddy **v2.11.9 is a host systemd service** owning `*:80`/`*:443` and `127.0.0.1:2019` (not a Compose container) — never edit `/etc/caddy/Caddyfile` or restart it. Cloudflare zone + scoped API token; dedicated PoC domain; Stalwart pin **DISPUTED — REQUIRES APPROVAL**: this plan says v1.1.0 (2026-11-09), ADR-002/architecture overview say v1.0.3. PostgreSQL 15+ **deferred** for Phase 1A (Stalwart-only tests need no external DB). Tools dig/swaks/curl/jq. Security prereqs: least-privilege token, default-deny firewall (open only 22/25/80/443), throwaway secrets, disposable data, STARTTLS via ACME, audit logging retained. **Upgrade caveat:** v1.1.0 adds passkey permissions to default roles; if upgrading from v1.0.x, set `STALWART_UPDATE_ROLE_PERMISSIONS=true` once during migration. **Port 25 is free on host with no listener but externally FILTERED** (Tencent SG + UFW change required and approval-gated); the owner reports UFW currently allows only 22/80/443. External DNS baseline 2026-11-18 unchanged from 2026-11-16 (no MX/A/AAAA/SPF/DMARC/DKIM; `mail.` absent).

## 3. Port 25 Inbound Validation (DBX-25)
1. Verify existing VPS `vps-tencent3b` public IP (`43.153.206.84`, VERIFIED via metadata) + PTR record (`NOT VERIFIED` — not yet queried).
2. **[approval-gated]** UFW default deny; allow 22/25; enable. Preflight 2026-11-18: UFW is enabled but currently allows only 22/80/443 per owner evidence; live rule list `NOT VERIFIED` via OpenChamber (sudo password required).
3. Confirm no upstream block: external `nc -vz <ip> 25`; document provider port-25 policy. Preflight 2026-11-18 external probe: TCP/25 **FILTERED/TIMEOUT** from OpenChamber network (consistent with SG/UFW not yet open); 22/80/443 OPEN. This is one vantage point and does not prove global reachability.
4. Deploy Stalwart Docker bound 0.0.0.0:25 with PoC domain.
5. Enable SMTP+submission, STARTTLS.
6. External send via swaks; verify 250 OK + message stored + raw EML retrievable.
7. Capture evidence: transcript, `ss -lntp`, logs, headers.
Pass: external delivery accepted/stored, port 25 reachable, STARTTLS negotiates. Fail: port blocked upstream, TLS/auth refusal, or not stored. Rollback: stop container, close 25.

## 4. Cloudflare DNS/MX Prerequisites
1. **[approval-gated]** Use existing zone `sintaksis.biz.id`; obtain scoped API token with DNS:Edit permission.
2. **[approval-gated]** Baseline: A `mail.sintaksis.biz.id` → VPS IP; no MX initially.
3. Conflict check (DBX-31): `dig MX sintaksis.biz.id`; if any `route*.mx.cloudflare.net` → CONFLICT_CLOUDFLARE_ROUTING, halt, show subdomain guidance; else proceed.
4. **[approval-gated]** Add records: MX (priority 10) → `mail.sintaksis.biz.id`, SPF TXT, DMARC TXT, DKIM TXT from Stalwart.
5. Verify propagation.
6. Document TTLs + record set.
Pass: MX resolves to Stalwart; SPF/DKIM/DMARC present. Fail: unreconcilable Cloudflare routing or propagation failure. Rollback: delete added DNS records, revoke token. **Note:** DNS state recorded; application conflict-detection path NOT exercised.

## 5. Stalwart Trial Design
Docker Compose: Stalwart + PostgreSQL (metadata; blobs local volume for PoC). Admin via env; no public signup. Account/alias provisioning via Stalwart Management API (UNVERIFIED — see §13); standard JMAP `Mailbox/get` is read-only folder listing, NOT account/alias creation. Short TTL (60 min) to exercise expiry. TLS via ACME. Scenarios: (1) create alias via Management API -> SMTP reachable; (2) inbound -> raw EML stored/parseable; (3) JMAP list -> count/headers; (4) delete alias -> 550; (5) 10 parallel alias creations -> no race/duplicate.

## 6. JMAP Checks
JMAP-01 auth 200+session; JMAP-02 Mailbox/get list; JMAP-03 create alias via `x:Account/set` (Management API) -> new id; JMAP-04 Email/get raw RFC822; JMAP-05 delete -> gone; JMAP-06 state change token; JMAP-07 invalid id -> 400/404 typed. Pass: all seven expected; state tokens usable.

## 7. Lifecycle Experiments (DBX-21/29/30/31)

### Phase-1A (Stalwart-only, testable now)
7.1a DBX-29 (US-017 temp mailbox — Stalwart subset): create account/alias via Management API (UNVERIFIED §13); verify SMTP reachable; inbound delivery works; manual delete → 550 rejection. Pass: create+live+delivery+delete.
7.4a DBX-31 (US-019 conflict — DNS inspection only): enumerate DNS state for `sintaksis.biz.id` (MX/A/TXT/NS); document Cloudflare Email Routing conflict detection logic; record DNS state. **Note:** DNS inspection does NOT prove DomiBox application-level conflict-detection logic works; application positive/conflict path NOT exercised. Pass: DNS state enumerated; conflict pattern documented.

### Phase-1B (App-dependent, BLOCKED until DomiBox code exists)
7.1b DBX-29 TTL metadata: set `expires_at` + `is_permanent=false`; verify auto-expiry enforcement. Requires DomiBox scheduler.
7.2 DBX-21 (US-009 auto-purge): seed N expired mailboxes+messages; scheduler 60s; verify messages deleted DB+engine, mailbox PURGED, audit row, no table lock >2s, non-expired untouched. Pass: within one cycle, locks<2s, audit recorded.
7.3 DBX-30 (US-018 conversion): temp->permanent; `expires_at=NULL`, `is_permanent=true`, quota 100MB (proposed, owner confirm); alias persists; messages retained; no duplicate. Pass: atomic conversion, quota applied, no orphan.
7.4b DBX-31 conflict-hold: domain with Cloudflare routing MX → application detection+hold+guidance; clean domain → normal activation; DNS failure → error path. Requires DomiBox application code.

## 8. RAM/CPU Benchmark (DBX-26)
Method: baseline idle 5 min (RSS/CPU); load 10/50/100 msg/min 10 min each + concurrent JMAP reads; metrics docker stats, vmstat, pg_stat_activity, Stalwart metrics; record peak RSS, avg CPU, disk I/O, p50/p95 latency; vary VPS size if budget. Proposed pass (owner confirm): baseline idle RSS measured; under 100 msg/min RSS growth <50% of baseline (to be determined from measurements), CPU<80% sustained, p95<5s, no OOM; no crash in 30-min soak. Fail: OOM, CPU>90% sustained, p95>10s, crash. Output: benchmark report + min VPS tier recommendation.

## 9. Cleanup & Rollback
Per-run reversible shutdown: `docker compose -p domibox-poc stop` (preserves volumes/data). Explicit data destruction (approval-gated): `docker compose -p domibox-poc down -v` ONLY after owner approval; deletes PoC-specific volumes. **Resource ownership check:** all cleanup commands MUST verify resource ownership (e.g., `docker volume ls | grep domibox-poc`) before deletion; NEVER touch volumes/networks/containers belonging to other services. Delete added DNS records; revoke token; close firewall ports verify ufw; archive logs/evidence. Triggers: any fail, security incident, cost overrun. Procedure: stop services, revert DNS, component-scoped rollback (NO VPS destruction), document incident+lessons.

## 10. Pass/Fail Criteria

### Phase-1A (Stalwart-only, PASS gates)
PASS only if ALL: (1) port 25 reachable + delivery accepted/stored (DBX-25) — **preflight status `BLOCKED`: 25 currently FILTERED externally with no host listener; requires SG+UFW approval**; (2) Cloudflare DNS/MX configured + DNS state recorded (DBX-31: **note:** DNS inspection does NOT prove DomiBox conflict-detection application logic works; application positive/conflict path NOT exercised; conflict path NOT TESTABLE until a simulated `route*.mx.cloudflare.net` record exists); (3) Stalwart scenarios 1-5 pass; (4) JMAP-01..07 pass; (5) lifecycle 7.1a (DBX-29 Stalwart subset: create+live+delivery+delete) + 7.4a (DBX-31 DNS inspection) pass; (6) benchmark meets pass (DBX-26); (7) security prereqs satisfied, no secret leak; (8) evidence captured. Any FAIL -> Phase-1A FAILS; document in risk register; decide remediate or descope. **Infrastructure readiness gate is PASS (`VERIFIED` 2026-11-18); the remaining gates are approval-gated / `NOT VERIFIED`, not infrastructure failures.**

### Phase-1B (App-dependent, BLOCKED until DomiBox code exists)
Lifecycle 7.1b (DBX-29 TTL metadata), 7.2 (DBX-21 auto-purge scheduler), 7.3 (DBX-30 temp->permanent conversion), and 7.4b (DBX-31 conflict-hold application logic) require DomiBox application code that does not exist yet. These tests are **BLOCKED** and cannot be executed during Phase-1 PoC. They will be deferred to Phase-2 integration testing after the application layer is implemented.

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
