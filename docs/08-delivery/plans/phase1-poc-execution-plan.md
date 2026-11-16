# Phase 1 PoC Execution Plan — DomiBox

| Status | Versi | Tanggal | Penulis | Dokumen Terkait |
| --- | --- | --- | --- | --- |
| PROPOSED | 0.1 | 2026-11-16 | omp-orchestrator/DeliveryDocs | bootstrap-status-report.md, epic-catalogue.md, recovery-state.md, jira-sync-map.json, ADR-001..ADR-012, traceability-matrix.md |

> No PoC step executed yet; all stories To Do; no benchmark/infra evidence.

## 1. Objectives
Validate three feasibility gates blocking implementation: (1) inbound mail reachability on port 25 + Stalwart SMTP acceptance (DBX-25); (2) resource envelope Stalwart+PostgreSQL within VPS RAM/CPU (DBX-26); (3) lifecycle correctness create/expiry/purge/permanent-conversion (DBX-21/29/30/31). Secondary: JMAP read/write, Cloudflare DNS/MX prereqs, rollback/cleanup, single pass/fail verdict with evidence. Out of scope: dashboard, Telegram, OTP extraction, sanitization, observability hardening, release cutover.

## 2. Environment & Prerequisites
VPS Ubuntu 22.04+ public IP; Cloudflare zone + scoped API token; dedicated PoC domain; Docker Compose v2; Stalwart latest stable; PostgreSQL 15+; tools dig/swaks/curl/jq. Security prereqs: dedicated PoC VPS/domain, least-privilege token, default-deny firewall (open only 22/25/80/443), throwaway secrets, disposable data, STARTTLS via ACME, audit logging retained.

## 3. Port 25 Inbound Validation (DBX-25)
1. Provision VPS; verify public IP + PTR.
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
Docker Compose: Stalwart + PostgreSQL (metadata; blobs local volume for PoC). Admin via env; no public signup. Aliases via JMAP create/list/delete. Short TTL (60 min) to exercise expiry. TLS via ACME. Scenarios: (1) create alias via JMAP -> SMTP reachable; (2) inbound -> raw EML stored/parseable; (3) JMAP list -> count/headers; (4) delete alias -> 550; (5) 10 parallel alias creations -> no race/duplicate.

## 6. JMAP Checks
JMAP-01 auth 200+session; JMAP-02 Mailbox/get list; JMAP-03 create alias -> new id; JMAP-04 Email/get raw RFC822; JMAP-05 delete -> gone; JMAP-06 state change token; JMAP-07 invalid id -> 400/404 typed. Pass: all seven expected; state tokens usable.

## 7. Lifecycle Experiments (DBX-21/29/30/31)
7.1 DBX-29 (US-017 temp mailbox): create 60-min TTL; alias live via JMAP; inbound works; expires_at set; is_permanent=false. Pass: created+live+TTL+delivery.
7.2 DBX-21 (US-009 auto-purge): seed N expired mailboxes+messages; scheduler 60s; verify messages deleted DB+engine, mailbox PURGED, audit row, no table lock >2s, non-expired untouched. Pass: within one cycle, locks<2s, audit recorded.
7.3 DBX-30 (US-018 conversion): temp->permanent; expires_at=NULL, is_permanent=true, quota 100MB (proposed, owner confirm); alias persists; messages retained; no duplicate. Pass: atomic conversion, quota applied, no orphan.
7.4 DBX-31 (US-019 conflict): domain with Cloudflare routing MX -> detection+hold+guidance; clean domain -> normal activation; DNS failure -> error path documented. Pass: conflict detected/guided, clean works, failure handled.

## 8. RAM/CPU Benchmark (DBX-26)
Method: baseline idle 5 min (RSS/CPU); load 10/50/100 msg/min 10 min each + concurrent JMAP reads; metrics docker stats, vmstat, pg_stat_activity, Stalwart metrics; record peak RSS, avg CPU, disk I/O, p50/p95 latency; vary VPS size if budget. Proposed pass (owner confirm): idle RSS <512MB total; under 100 msg/min RSS<1.5GB, CPU<80% sustained, p95<5s, no OOM; no crash in 30-min soak. Fail: OOM, CPU>90% sustained, p95>10s, crash. Output: benchmark report + min VPS tier recommendation.

## 9. Cleanup & Rollback
Per-run: docker compose down -v; delete DNS records/zone; revoke token; close firewall ports verify ufw; remove volumes/images; archive logs/evidence before destroy. Triggers: any fail, security incident, cost overrun. Procedure: stop services, revert DNS, destroy/restore VPS, document incident+lessons.

## 10. Pass/Fail Criteria (Phase 1 overall)
PASS only if ALL: (1) port 25 reachable + delivery accepted/stored (DBX-25); (2) Cloudflare DNS/MX configured + conflict path exercised (DBX-31); (3) Stalwart scenarios 1-5 pass; (4) JMAP-01..07 pass; (5) lifecycle 7.1-7.4 pass; (6) benchmark meets pass (DBX-26); (7) security prereqs satisfied, no secret leak; (8) evidence captured. Any FAIL -> Phase 1 FAILS; document in risk register; decide remediate or descope.

## 11. Dependencies & Risks
Cloud provider port-25 policy (verify before provisioning; fallback provider); Cloudflare routing conflict (subdomain strategy DBX-31); Stalwart version stability (pin version); PostgreSQL RAM (benchmark first); DNS propagation (low TTL + wait scripts); single-owner VPS no HA (acceptable PoC); unverified proposed values quota/TTL (owner confirmation gate). Jira: DBX-25, DBX-26, DBX-21, DBX-29, DBX-30, DBX-31, DBX-13, DBX-11.

## 12. Evidence & Reporting
Evidence under docs/08-delivery/poc-evidence/ (create during execution) or attached to Jira. Final report docs/08-delivery/phase1-poc-report.md after execution. This plan stays PROPOSED until execution; update Status to EXECUTED with results appended.
