# Phase 1 PoC Preflight Report — DomiBox

**Date:** 2026-11-18 (live VPS reconciliation)
**Status:** READY FOR CONTROLLED POC — **CONDITIONAL / APPROVAL-GATED**
**Scope:** READ-ONLY infrastructure verification. No deployment, no firewall/Security Group/DNS changes, no container or Caddy modification was performed in this assignment.

> **Supersedes the 2026-11-16 snapshot.** The previous `PARTIALLY READY` assessment was based on an SSH timeout from the OMP execution environment. That timeout was environmental, not a VPS fault. OpenChamber can invoke a local Windows terminal with access to the existing SSH config, and `ssh -o BatchMode=yes -o ConnectTimeout=10 vps-tencent3b` now succeeds. The owner's independently observed evidence (kernel 6.8.0-138-generic, Docker 29.9.3, Compose v5.7.0, UFW active on 22/80/443, Caddy on 80/443) is corroborated below.

**Status legend used throughout:** `VERIFIED` (observed directly in this assignment) · `NOT VERIFIED` (not tested / no evidence) · `BLOCKED` (cannot proceed without an external gate) · `PROPOSED` (design recommendation, not executed) · `REQUIRES APPROVAL` (owner action required before execution).

---

## 1. Verified VPS Inventory (`VERIFIED`)

**Observation time:** 2026-11-18T14:23:06Z (UTC). **Method:** non-interactive SSH (`BatchMode=yes`) from the OpenChamber local terminal; read-only commands only.

| Item | Observed value | Status |
| --- | --- | --- |
| Hostname / kernel | `VM-0-4-ubuntu` · `6.8.0-138-generic #138-Ubuntu SMP PREEMPT_DYNAMIC` | `VERIFIED` |
| CPU | 2 vCPU · AMD EPYC 7K62 48-Core Processor · x86_64 | `VERIFIED` |
| Uptime / load | up 7 days 21:33 · load average `0.01, 0.04, 0.00` | `VERIFIED` |
| Memory | total 3.6 GiB · used 1.4 GiB · free 293 MiB · buff/cache 2.3 GiB · **available 2.3 GiB** | `VERIFIED` |
| Swap | `/swap.img` 1.9 GiB (2,035,708 KiB) · used 524 KiB (negligible) | `VERIFIED` |
| Disk (root `/dev/vda2`) | 59 GB total · 9.2 GB used · **48 GB available** · 17% use | `VERIFIED` |
| Inodes (root) | 3,932,160 total · 289,027 used · 3,643,133 free · 8% use | `VERIFIED` |
| System time | `2026-11-18T14:23:06Z` · local `Wed 2026-11-18 22:23:06 CST` · timezone `Asia/Shanghai (CST, +0800)` · NTP active, clock synchronized | `VERIFIED` |
| Docker | 29.9.3 (build 5457199), storage driver `overlayfs` | `VERIFIED` |
| Docker Compose | v5.7.0 | `VERIFIED` |
| Docker daemon | 1 container (1 running), 2 images, 0 paused/stopped | `VERIFIED` |
| Reverse proxy | Caddy v2.11.9, host systemd service, config `/etc/caddy/Caddyfile` | `VERIFIED` |
| Cloud instance | `ins-f6b2sjfy` · public IP `43.153.206.84` (metadata, read-only) | `VERIFIED` |

**Reconciliation note:** the owner's snapshot reported `2.2 GiB available` and `48 GB available`; the live check reports `2.3 GiB available` and `48 GB available`. The figures are consistent within normal fluctuation. The VPS is **up, provisioned, and healthy** — it must not be described as down or unprovisioned.

---

## 2. Port Occupancy Matrix (`VERIFIED`)

Host listeners from `ss -tlnp` at 2026-11-18T14:23:06Z, cross-checked with external TCP probes from the OpenChamber network.

| Port / bind | Owner / process | Host state | External probe | DomiBox implication |
| --- | --- | --- | --- | --- |
| `0.0.0.0:22`, `[::]:22` | OpenSSH (host) | LISTEN | **OPEN** | Admin access. Leave untouched. |
| `*:80` | Caddy (host systemd, v2.11.9) | LISTEN | **OPEN** | **Occupied** — do not bind. Reuse via reverse proxy only. |
| `*:443` | Caddy (host systemd, v2.11.9) | LISTEN | **OPEN** | **Occupied** — do not bind. Reuse via reverse proxy only. |
| `127.0.0.1:2019` | Caddy admin API (default) | LISTEN | not probed (loopback) | Private; leave untouched. |
| `127.0.0.53:53`, `127.0.0.54:53` | systemd-resolved | LISTEN | not probed (loopback) | Leave untouched. |
| `127.0.0.1:9000`, `127.0.0.1:9001` | `rustfs` container (existing, unrelated) | LISTEN | not probed (loopback) | **Must remain untouched.** No bind conflict. |
| `127.0.0.1:5678` | Unrelated local listener (not inspected) | LISTEN | not probed (loopback) | Not inspected per scope; leave untouched. |
| **TCP/25** | **none** | **NO LISTENER** | **FILTERED / TIMEOUT** | Free on host; externally blocked. Eligible for PoC only after approval. |
| 465, 587, 993, 143, 110, 995, 2525, 8080, 8081, 5432 | none | no listeners | not probed | Keep closed/private. Management endpoints stay Docker-internal. |

**Conclusion:** the only host-port collision risk for the PoC is 80/443, already owned by Caddy. Port 25 is free at the host level. The external `FILTERED/TIMEOUT` result on port 25 is consistent with the owner's evidence that UFW does not allow 25 and the Tencent Security Group has not been opened; it is a **single-vantage-point observation and does not prove global reachability**.

**SMTP reachability:** `NOT VERIFIED`. No external SMTP banner/`250 OK` test was performed because there is no active authorized listener and no inbound approval. Per assignment constraints, SMTP inbound reachability must not be claimed until tested against an active authorized listener.

---

## 3. Docker Resource Assessment (`VERIFIED`)

| Resource | Observed | Assessment |
| --- | --- | --- |
| Existing container | `rustfs` (`rustfs/rustfs:1.0.4`), Up 7 days, `127.0.0.1:9000-9001->9000-9001/tcp` | Unrelated, isolated, loopback-only. Do not modify. |
| rustfs utilization | 0.40% CPU · 76.36 MiB / 3.637 GiB (2.05%) · NET 178 kB / 1.39 MB · BLOCK 209 kB / 7.2 MB | Negligible. |
| Docker volumes | none present | Clean slate; PoC can create its own prefixed volumes. |
| Docker networks | `bridge`, `host`, `none`, `rustfs_default` | PoC must create a dedicated network; never join `rustfs_default`. |
| RAM headroom | 2.3 GiB available before any PoC workload | Sufficient for Stalwart plus optional PostgreSQL. |
| Disk / inode headroom | 48 GB free · 8% inode use | Ample for the documented 10 GB DomiBox quota. |
| Load | ~0.01 | No contention. |

`docs/03-architecture/capacity-planning.md` budgets ≤1.2 GiB peak for the full future DomiBox stack. The initial PoC (Stalwart alone) is well inside that envelope. **Docker/Compose readiness gate: PASS.**

---

## 4. DNS Baseline — Current vs 2026-11-16 (`VERIFIED`)

**Method:** DNS-over-HTTPS to `https://dns.google/resolve`, queried 2026-11-18. Previous baseline from `docs/08-delivery/phase1-preflight-report.md` (2026-11-16T08:35:20Z). **No Cloudflare changes were made.**

| Record / name | 2026-11-18 (current) | 2026-11-16 baseline | Delta |
| --- | --- | --- | --- |
| MX `sintaksis.biz.id` | NOERROR, no answer (none) | none | unchanged |
| A `sintaksis.biz.id` | NOERROR, no answer (none) | none | unchanged |
| AAAA `sintaksis.biz.id` | NOERROR, no answer (none) | not queried | new query, none |
| NS `sintaksis.biz.id` | `dylan.ns.cloudflare.com`, `kristina.ns.cloudflare.com` | same | unchanged |
| TXT `sintaksis.biz.id` (SPF) | NOERROR, no answer (none) | none | unchanged |
| TXT `_dmarc.sintaksis.biz.id` (DMARC) | NXDOMAIN | NXDOMAIN | unchanged |
| TXT `default._domainkey.sintaksis.biz.id` (DKIM) | NXDOMAIN | not queried | new query, none |
| A / AAAA `mail.sintaksis.biz.id` | NXDOMAIN | not queried | new query, none |

**Interpretation:** the zone is still clean — no MX, no apex A/AAAA, no SPF, no DMARC, no DKIM, and no `mail` host. Cloudflare Email Routing is **not** enabled (no `route*.mx.cloudflare.net` MX records). This preserves the planned DNS path.

**Caveat (unchanged from 2026-11-16):** inspecting specific names/types does not prove the entire zone or all subdomains are absent. DKIM was probed with the common `default` selector; a different selector may exist but is `NOT VERIFIED`.

---

## 5. Firewall & Security Group Baseline

| Layer | Evidence | Status |
| --- | --- | --- |
| UFW | `/etc/ufw/ufw.conf` → `ENABLED=yes`. `sudo -n ufw status verbose` failed ("a password is required"), so the live rule list could not be read non-interactively. Owner-provided evidence: allowed 22, 80, 443; TCP/25 not allowed. | `VERIFIED` enabled · rule detail `NOT VERIFIED` via OpenChamber (owner evidence accepted) |
| Tencent Security Group | `tccli` not installed and no console access from this environment; instance metadata (`ins-f6b2sjfy`, `43.153.206.84`) does not expose SG rules. External probe shows 22/80/443 open, 25 filtered. | `NOT VERIFIED` (read-only CLI unavailable) — requires owner console check |
| TCP/25 external | FILTERED/TIMEOUT from OpenChamber network; no listener on host | `VERIFIED` from one vantage point; global reachability `NOT VERIFIED` |

No UFW, Security Group, or DNS changes were made.

---

## 6. Existing Caddy Coexistence Strategy (`PROPOSED` / `REQUIRES APPROVAL`)

Caddy is a **host systemd service** (v2.11.9, `/etc/caddy/Caddyfile`) owning `*:80` and `*:443`, with its admin API on `127.0.0.1:2019`. This differs from the architecture docs, which depict Caddy as a container inside the Compose stack (`docs/03-architecture/architecture-overview.md` §3.2). The live reality takes precedence for the PoC.

Design rules for the isolated PoC:

1. **Preserve Caddy.** Do not edit `/etc/caddy/Caddyfile`, do not restart Caddy, and do not bind 80/443.
2. **No host-port collision.** Stalwart binds only `0.0.0.0:25` on the host (when approved). All other Stalwart ports stay inside the Compose network.
3. **Private management by default.** JMAP/admin, PostgreSQL (if enabled), and any submission listener are Docker-network-only with **no host publish**. Optional debug binds are restricted to `127.0.0.1` and disabled by default.
4. **Reuse Caddy only when appropriate.** If HTTPS access to Stalwart JMAP/admin is later needed, add a path-based `reverse_proxy` stanza (e.g. `/jmap/*` → `127.0.0.1:8081`) **only with owner approval and only in a separate, reviewable change**. It is not part of this assignment.
5. **Dedicated stack.** Compose project `domibox-poc`, dedicated network `domibox-poc_net`, named volumes prefixed `domibox-poc_`. No joins to `rustfs_default`; no references to rustfs or any unrelated workload.
6. **Independent rollback.** `docker compose -p domibox-poc stop` is reversible and preserves data. `docker compose -p domibox-poc down -v` requires an ownership check (`docker volume ls | grep domibox-poc`) **and explicit owner approval**. Never delete `rustfs` volumes, Caddy config, or shared resources.

---

## 7. Stalwart PoC Deployment Design (`PROPOSED` / `REQUIRES APPROVAL`)

| Element | Design | Status |
| --- | --- | --- |
| Compose project | `domibox-poc` (isolated) | `PROPOSED` |
| Services | `stalwart` only for Phase 1A; PostgreSQL deferred | `PROPOSED` |
| Host ports | `25:25` only (after approval). 80/443 untouched. | `PROPOSED` / `REQUIRES APPROVAL` |
| Internal ports | JMAP/admin `8081` Docker-network-only; no publish of 465/587/993/2525/5432 | `PROPOSED` |
| Storage | named volumes `domibox-poc_stalwart_data`, `domibox-poc_stalwart_config`; Stalwart internal storage for blobs | `PROPOSED` |
| Version pin | PoC plan pins **v1.1.0**; ADR-002 and architecture overview reference **v1.0.3**. Owner must decide the pin; v1.1.0 upgrade caveat (`STALWART_UPDATE_ROLE_PERMISSIONS=true` once) is documented. | `REQUIRES APPROVAL` |
| Admin | throwaway credentials, no public signup, private endpoints only | `PROPOSED` |
| TLS | SMTP STARTTLS + ACME certificate (approval-gated); HTTPS via existing Caddy only if explicitly added | `REQUIRES APPROVAL` |
| DNS prerequisites | A `mail.sintaksis.biz.id` → `43.153.206.84`, MX → `mail` (priority 10), SPF, DMARC, DKIM from Stalwart | `REQUIRES APPROVAL` |
| Rollback | stop (reversible) / `down -v` only after ownership check + approval | `PROPOSED` |

---

## 8. Technical Feasibility Gates (Step 6)

| # | Gate | Status | Basis |
| --- | --- | --- | --- |
| 1 | Resource headroom | `VERIFIED` — PASS | 2.3 GiB RAM available, 48 GB disk, 8% inode, load ~0.01 |
| 2 | Port conflicts | `VERIFIED` — PASS for 25 | 25 free on host; 80/443 owned by Caddy and must be avoided |
| 3 | Inbound SMTP port 25 eligible for later testing | `BLOCKED` | Externally FILTERED; Tencent SG rule + UFW allow required; no active listener to test against |
| 4 | Stalwart version & Management API | `NOT VERIFIED` / `REQUIRES APPROVAL` | v1.1.0 endpoints (`x:Account/set`, `x:Alias/set`) still unverified (plan §13); version pin conflict must be decided |
| 5 | PostgreSQL necessary for initial PoC | `PROPOSED` — NOT necessary | Stalwart-only stalwart tests need no external DB; PostgreSQL belongs to Phase 1B app integration |
| 6 | Temporary alias mapping | `PROPOSED` — dedicated mailbox per alias in Stalwart | Simplest isolated PoC structure; avoids shared-mailbox data bleed; distinct from ADR-003 virtual-alias model, which is an app-layer decision |
| 7 | Tests possible with Stalwart alone | `PROPOSED` | SMTP acceptance on 25, inbound delivery + raw EML storage, JMAP read/list, management-API account/alias create-delete (once verified), STARTTLS negotiation |
| 8 | Tests requiring DomiBox application code | `BLOCKED` | TTL auto-expiry (7.1b), auto-purge scheduler (7.2), temp→permanent conversion (7.3), DNS conflict-hold logic (7.4b) — all Phase 1B |

All untested capabilities above remain explicitly `NOT VERIFIED`; no capability is upgraded to verified by this preflight.

---

## 9. Required Firewall / Security Group Changes (`REQUIRES APPROVAL`)

- [ ] **Tencent Security Group:** add inbound TCP/25 (scope to known sender CIDRs if available, else `0.0.0.0/0` per ADR-010) for `ins-f6b2sjfy`. Keep 22 restricted to admin IPs; 80/443 already open.
- [ ] **UFW:** allow `25/tcp` on the host (currently not allowed per owner evidence); keep 22/80/443; keep default-deny inbound. **Not executed here.**
- [ ] **Cloudflare DNS:** add A `mail.sintaksis.biz.id` → `43.153.206.84`; MX `sintaksis.biz.id` → `mail` (10); TXT SPF `v=spf1 ip4:43.153.206.84 -all`; TXT DMARC `v=DMARC1; p=none; rua=mailto:admin@sintaksis.biz.id`; TXT DKIM from Stalwart. Use DNS_ONLY (grey cloud) for MX/A.
- [ ] **VPS:** deploy the `domibox-poc` Stalwart container (only after the above are approved and this is re-scoped as an execution task).

No changes in this list were applied during this assignment.

---

## 10. Exact Changes Requiring Owner Approval (`REQUIRES APPROVAL`)

1. Decision: pin Stalwart **v1.1.0** (PoC plan) vs **v1.0.3** (ADR-002 / architecture overview).
2. Authorize opening inbound TCP/25 in the Tencent Security Group and UFW.
3. Authorize the five Cloudflare DNS records above (zone `sintaksis.biz.id` is pre-existing — never delete the zone or pre-existing records).
4. Authorize deployment of the isolated `domibox-poc` Stalwart stack and throwaway PoC credentials.
5. Authorize the temporary-alias structure (dedicated mailbox per alias) for Phase 1A.
6. Authorize any later Caddy reverse-proxy stanza for Stalwart HTTPS/JMAP (separate change).
7. Confirm acceptance of data-destruction rollback (`down -v`) only after ownership verification.
8. Confirm owner verification of the live UFW rule list (sudo required; not readable non-interactively here).

---

## 11. Jira Coverage Decision (preserved from 2026-11-16)

- **OPS-001 (admin auth)** and **OPS-004 (rate limiting)** remain story-level gaps with epic-level DBX-8 / EPIC-07 coverage. `NO NEW JIRA ITEMS` decision is retained.
- VPS reachability does **not** close any implementation story; all PoC stories remain `To Do`. Implementation stories are not closed merely because the VPS is reachable.
- Sync map: DBX-8 (EPIC-07) covers OPS-001/OPS-004 at epic level; RTM records the story-level GAP.

---

## 12. Final Verdict

### READY FOR CONTROLLED POC — CONDITIONAL ON OWNER APPROVALS

**`VERIFIED`**
- SSH access from OpenChamber local terminal (`BatchMode=yes`); previous timeout was environmental.
- Full VPS inventory: kernel 6.8.0-138-generic, 2 vCPU EPYC 7K62, 3.6 GiB RAM / 2.3 GiB available, 1.9 GiB swap, 48 GB disk / 8% inode, NTP-synced time.
- Docker 29.9.3 + Compose v5.7.0; one unrelated `rustfs` container; no volumes; ample headroom.
- Port 25 free on host; no listener; externally FILTERED from OpenChamber network; 22/80/443 OPEN.
- Caddy v2.11.9 (host systemd) owns 80/443 + 2019 admin — confirmed, not a Compose container.
- DNS unchanged from 2026-11-16: no MX/A/AAAA/SPF/DMARC/DKIM; `mail.` absent; Cloudflare NS intact.

**`NOT VERIFIED`**
- Tencent Security Group rules (no read-only CLI/console access).
- Live UFW rule list (sudo password required; owner evidence accepted).
- Stalwart Management API endpoints/auth/permissions (plan §13).
- SMTP inbound acceptance / `250 OK` (no active authorized listener).
- Global (multi-vantage) SMTP reachability.

**`BLOCKED`**
- Phase 1A execution until firewall/DNS/version/deployment approvals are recorded.
- Phase 1B (TTL expiry, auto-purge, permanent conversion, conflict-hold) until DomiBox application code exists.

**`PROPOSED`**
- Caddy coexistence design, isolated `domibox-poc` Compose design, deferral of PostgreSQL, dedicated-mailbox alias structure, Stalwart-only vs app-dependent test split.

**Go / No-Go:** **GO** for a controlled, isolated Stalwart PoC once the §9/§10 approvals are recorded and executed under a separate authorized task. **NO-GO** for any deployment, firewall, DNS, or Caddy change within this read-only assignment. This preflight alone does not close Jira implementation stories.

---

## 13. Evidence Appendix

**SSH validation (OpenChamber local terminal):**
```
$ ssh -o BatchMode=yes -o ConnectTimeout=10 vps-tencent3b "echo SSH_OK"
SSH_OK
```

**External TCP probe (OpenChamber network → 43.153.206.84):**
```
TCP 22  -> OPEN
TCP 25  -> FILTERED/TIMEOUT
TCP 80  -> OPEN
TCP 443 -> OPEN
```

**Host listeners (`ss -tlnp`, 2026-11-18T14:23:06Z):** `127.0.0.53:53`, `127.0.0.54:53`, `127.0.0.1:9000`, `127.0.0.1:9001`, `127.0.0.1:5678`, `0.0.0.0:22`, `[::]:22`, `127.0.0.1:2019`, `*:443`, `*:80`. No listener on `:25`.

**Caddy:** `systemctl is-active caddy` → `active`; `pgrep -a caddy` → `/usr/bin/caddy run --environ --config /etc/caddy/Caddyfile`; `caddy version` → `v2.11.9`.

**Docker:** `ServerVersion=29.9.3 Containers=1 Running=1 Images=2 Driver=overlayfs`; `rustfs  0.40%  76.36MiB / 3.637GiB  2.05%`; `docker volume ls` empty.

**DNS (DoH, 2026-11-18):** MX/A/AAAA/TXT apex → NOERROR no answer; NS → Cloudflare pair; `_dmarc`, `default._domainkey`, `mail.` → NXDOMAIN.

**Prior baseline preserved:** 2026-11-16T08:35:20Z DNS raw responses and the OMP SSH timeout log are retained in version history; they are not deleted, only superseded.

---

**Report author:** OpenChamber (Phase 1A live reconciliation)
**Report date:** 2026-11-18
**Status:** READY FOR CONTROLLED POC — CONDITIONAL / APPROVAL-GATED
