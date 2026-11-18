# Stage A — controlled private Stalwart PoC evidence

**Date:** 2026-11-18 (UTC) · **Verdict: STAGE A PASS** — private Stalwart operations verified on the real server.
**Scope:** one isolated `domibox-poc` container on `vps-tencent3b`, loopback-only SMTP/management. No public exposure, DNS, firewall or Caddy changes.

Raw sanitized runner report: `stage-a-local-report.json`. No credentials, tokens, URL userinfo or generated account passwords appear in these files.

## 1–3. Deployment and isolation

| Item | Observed |
| --- | --- |
| Image | `stalwartlabs/stalwart:v1.1.1`, digest `sha256:5ebdf474b237161742fe4309396af4ae8797c938e8e6eb7e2d4837332c4f9851` |
| Version | Stalwart **1.1.1** (logged at startup) |
| Compose project | `domibox-poc`, network `domibox-poc_net`, volumes `domibox-poc_etc` / `domibox-poc_data` |
| Container | `domibox-poc-stalwart`, health `healthy` while running, 0 restarts, exit code 0 |
| Published ports | `127.0.0.1:25->25/tcp`, `127.0.0.1:8080->8080/tcp` only |
| Tunnels used | local `18080 -> VPS 127.0.0.1:8080`, local `2525 -> VPS 127.0.0.1:25` |
| Pre-deploy occupancy | 25 and 8080 free; Caddy owned 80/443; no pre-existing `domibox-poc*` resources |
| Bootstrap | `x:Bootstrap/set` via JMAP: hostname `mail.sintaksis.biz.id`, domain `sintaksis.biz.id`, RocksDB, internal directory, `Stdout` tracer, manual DNS, `requestTlsCertificate=false`, `generateDkimKeys=false`; container restarted out of bootstrap mode |

## 4–9. Real test results (from `stage-a-local-report.json`)

| Test | Result | Actual evidence |
| --- | --- | --- |
| T-001 JMAP session / capabilities | **PASS** | Session at `/.well-known/jmap`; core, mail, calendars, sieve, websocket and other capabilities advertised |
| T-T01 STARTTLS advertised | **PASS** | EHLO advertised `STARTTLS`, `SMTPUTF8`, `SIZE`, `REQUIRETLS` |
| T-T02 STARTTLS negotiation | **PASS** | Negotiation succeeded through the SSH tunnel |
| T-T03 Certificate state | **PASS (explicit skip)** | `certificate verification intentionally skipped for authorized PoC` — **not** a verification PASS |
| T-T04 Plain SMTP acceptance | **BLOCKED** | Not requested; plaintext is never reported as a TLS result |
| T-002 Domain discovery | **PASS** | `sintaksis.biz.id -> id b` |
| T-003 Identity creation | **PASS** | Run-owned id `c`; alias `poc-alias-67fe6e3d07@sintaksis.biz.id`; readback verified |
| T-004 Delivery + retrieval | **PASS** | SMTP accepted in 2766 ms; JMAP visible in 250 ms; `poll_attempts=1`, subject and recipient matched, no timeout |
| T-005 Cleanup | **PASS** | Destroyed only run-owned id `c`; follow-up `x:Account/query` for `poc-` returned zero ids |

Overall status `PASS`, exit code 0, `live_functional_test=true`. SMTP acceptance and JMAP visibility are recorded as distinct measurements.

## 10–13. Cleanup, resources and unaffected services

| Item | Observed |
| --- | --- |
| Final container state | `Exited (0)` after component-scoped `docker compose ... stop`; volumes **preserved**; no `down -v` |
| Host memory before / after | 2.2–2.3 GiB available before; 2.1 GiB available after (short smoke test, no sustained load) |
| Host disk before / after | 48 GB free (17%) before; 47 GB free (18%) after |
| Container memory / CPU | 115.2 MiB (3.09% of 3.637 GiB), 0.00% CPU at observation |
| Container I/O | NET 68.7 MB / 275 kB; BLOCK 0 B / 4.67 MB |
| PoC volume sizes | `domibox-poc_etc` 122 B; `domibox-poc_data` 2.205 MB |
| Warnings | DNSSEC resolver warning (DANE disabled); no TLS certificates warning before bootstrap; no crash/restart |
| Unrelated services | Caddy `active` on `*:80`/`*:443`; `rustfs` still Up 7 days on `127.0.0.1:9000-9001`; no n8n container was present in `docker ps`; ports 25/8080 released after stop |

## 14. Live integration findings (corrections applied to the runner)

1. `GET /jmap/` returns 404. Session discovery is `GET /.well-known/jmap` (307 → `/jmap/session`). Runner updated.
2. Stalwart management `Foo/get` returns `list`, while standard mail `Email/get` returns `data`. Runner now accepts both.
3. `urn:stalwart:jmap` appears under `accounts[].accountCapabilities`, not in top-level `capabilities`. Capability check now uses the union of both.
4. Bootstrap can be completed entirely via `x:Bootstrap/set` with the internal directory; the console tracer variant is `@type: "Stdout"`.
5. `x:Account/set` create/destroy, `x:Domain/query` + `x:Domain/get`, `Email/query` + `Email/get` all behaved as documented.

## 15. Publication

Changes are committed only to `feat/phase1a-stalwart-poc`; PR #2 stays open/draft with base `docs/project-bootstrap`. PR #1 is unchanged. No merge was performed. Commit SHA is recorded in the final handoff message.

## 16. Stage B blockers (not authorized, not executed)

- Tencent Security Group inbound TCP/25 for `ins-f6b2sjfy`.
- UFW `allow 25/tcp`.
- Cloudflare A `mail`, MX, SPF, DMARC, DKIM records (DNS Only).
- Publish SMTP on `0.0.0.0:25` only after the above.
- Independent public-vantage evidence and a real external SMTP acceptance + JMAP retrieval test.
- No Stage B action is implied by this PASS.
