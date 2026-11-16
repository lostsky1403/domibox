# Phase 1 PoC Preflight Report — DomiBox

**Date:** 2026-11-16  
**Status:** PARTIALLY READY (DNS verified; SSH/VPS preflight BLOCKED)

---

## 1. DNS Baseline (VERIFIED)

**Method:** DNS-over-HTTPS (DoH) queries to `https://dns.google/resolve`  
**Timestamp:** 2026-11-16T08:20:136Z (UTC)  
**Domain:** sintaksis.biz.id

### Record Type Results

| Record Type | Query Name | Status | Answer | Notes |
|-------------|------------|--------|--------|-------|
| **MX** | sintaksis.biz.id | 0 (NOERROR) | **NONE** | No MX records exist |
| **A** | sintaksis.biz.id | 0 (NOERROR) | **NONE** | No A records exist |
| **AAAA** | sintaksis.biz.id | 0 (NOERROR) | **NONE** | No IPv6 records exist |
| **TXT** | sintaksis.biz.id | 0 (NOERROR) | **NONE** | No TXT records (no SPF/DMARC) |
| **DMARC** | _dmarc.sintaksis.biz.id | 3 (NXDOMAIN) | **NONE** | DMARC record does not exist |
| **mail subdomain** | mail.sintaksis.biz.id | 3 (NXDOMAIN) | **NONE** | mail.sintaksis.biz.id does not exist |
| **NS** | sintaksis.biz.id | 0 (NOERROR) | dylan.ns.cloudflare.com, kristina.ns.cloudflare.com | Cloudflare delegation confirmed |

### SOA Authority
```
dylan.ns.cloudflare.com. dns.cloudflare.com. 2420070819 10000 2400 604800 1800
```

### DNS Baseline Conclusion
- **MX:** NOT CONFIGURED (no mail routing)
- **SPF/DKIM/DMARC:** NOT CONFIGURED
- **A/AAAA:** NOT CONFIGURED (no web server)
- **Nameservers:** Cloudflare (dylan + kristina.ns.cloudflare.com)
- **Zone Status:** Active, delegated to Cloudflare, but no records configured

**Implication for PoC:** DNS is a clean slate. No conflicts with existing mail infrastructure. Cloudflare Email Routing is NOT enabled (no `route*.mx.cloudflare.net` MX records). PoC can proceed with DNS configuration without conflict detection (DBX-31 conflict path NOT exercised — clean domain).

---

## 2. VPS Preflight (BLOCKED — SSH Unreachable)

**Target:** vps-tencent3b (43.153.206.84)  
**Method:** SSH with BatchMode + ConnectTimeout=20s  
**Timestamp:** 2026-11-16T08:20:33Z (UTC)

### Connection Attempt
```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=no vps-tencent3b
```

### Result
```
kex_exchange_identification: read: Connection timed out
banner exchange: Connection to 43.153.206.84 port 22: Connection timed out
```

**Duration:** 19.31 seconds (timeout reached)

### Failure Analysis
- **SSH daemon:** Unreachable (no banner exchange)
- **Possible causes:**
  1. VPS powered off or suspended
  2. Firewall blocking port 22 (Tencent Security Group or iptables)
  3. SSH daemon not running
  4. Network routing issue (VPS IP changed or unreachable from current network)
  5. Tencent Cloud instance in stopped state

### VPS Preflight Conclusion
**STATUS: NOT VERIFIED** — Cannot confirm:
- CPU/RAM availability
- Disk space
- Docker/Compose installation
- Port 25/465/587/80/443/993 availability
- UFW/firewall configuration
- Existing workloads (rustfs container)

**Impact on PoC:** VPS readiness is UNKNOWN. Phase 1A (Stalwart deployment) CANNOT proceed until SSH access is restored and VPS preflight is completed.

---

## 3. Jira Coverage Decision (OPS-001/OPS-004)

### Current State
- **OPS-001 (admin auth):** Story-level GAP (no story with verified AC for master admin authentication)
- **OPS-004 (rate limiting):** Story-level GAP (no story with verified AC for rate limiting)
- **Epic-level coverage:** Both mapped to DBX-8 (EPIC-07 Security & HTML Sanitization)

### Decision: NO NEW JIRA ITEMS

**Rationale:**
1. **Epic coverage exists:** DBX-8 (EPIC-07) explicitly includes security controls that encompass authentication and rate limiting at the architectural level.
2. **Story-level gaps documented:** RTM (traceability-matrix.md) explicitly notes these as "story-level GAP, epic-level DBX-8/EPIC-07" with full transparency.
3. **Mission constraint:** "Create new Jira items only if genuinely missing" — epic-level coverage is sufficient for Phase 1 PoC scope.
4. **Phase 1 scope:** PoC focuses on mail engine feasibility (DBX-25/26/29/30/31), not dashboard authentication or rate limiting implementation.
5. **Future work:** Story-level AC for OPS-001/OPS-004 should be created during Phase 2 (application layer implementation), not Phase 1 (infrastructure PoC).

**Risk:** If Phase 1 PoC reveals authentication/rate-limiting requirements for Stalwart Management API access, new stories may be needed. This will be documented in the PoC report if encountered.

---

## 4. Infrastructure Changes Requiring Approval (NOT YET AUTHORIZED)

The following changes are **approval-gated** and MUST NOT be executed without explicit owner authorization:

### DNS Changes (Cloudflare)
- [ ] **Add A record:** `mail.sintaksis.biz.id` → `43.153.206.84` (or PoC subdomain)
- [ ] **Add MX record:** `sintaksis.biz.id` → `mail.sintaksis.biz.id` (priority 10)
- [ ] **Add TXT record (SPF):** `v=spf1 ip4:43.153.206.84 -all`
- [ ] **Add TXT record (DMARC):** `v=DMARC1; p=none; rua=mailto:admin@sintaksis.biz.id`
- [ ] **Add TXT record (DKIM):** (generated by Stalwart after deployment)

### Firewall Changes (Tencent Cloud Security Group)
- [ ] **Allow inbound TCP/25** (SMTP) from 0.0.0.0/0
- [ ] **Allow inbound TCP/465** (SMTPS) from 0.0.0.0/0
- [ ] **Allow inbound TCP/587** (Submission) from 0.0.0.0/0
- [ ] **Allow inbound TCP/80** (HTTP, for ACME challenge) from 0.0.0.0/0
- [ ] **Allow inbound TCP/443** (HTTPS, for JMAP/WebUI) from 0.0.0.0/0
- [ ] **Allow inbound TCP/993** (IMAPS) from 0.0.0.0/0
- [ ] **Verify TCP/22** (SSH) is already allowed (currently BLOCKED)

### VPS Changes (Ubuntu)
- [ ] **Install Docker Engine** (if not present)
- [ ] **Install Docker Compose v2** (if not present)
- [ ] **Configure UFW:** `ufw allow 22,25,80,443,465,587,993/tcp`
- [ ] **Deploy Stalwart v1.1.0** via Docker Compose (isolated project: `domibox-poc`)
- [ ] **Deploy PostgreSQL 16** via Docker Compose (same project)
- [ ] **Generate ACME certificates** via Let's Encrypt (requires port 80/443 open)
- [ ] **Configure Stalwart admin account** (throwaway credentials for PoC)
- [ ] **Create test domain** (sintaksis.biz.id or PoC subdomain)
- [ ] **Create test accounts** (1 temporary, 1 permanent)

### Rollback Plan (Component-Scoped)
- [ ] **Stop containers:** `docker compose -p domibox-poc down`
- [ ] **Remove volumes:** `docker volume rm domibox-poc_stalwart-data domibox-poc_postgres-data` (VERIFY OWNERSHIP FIRST)
- [ ] **Remove DNS records:** Delete A/MX/TXT records from Cloudflare
- [ ] **Close firewall ports:** Remove Security Group rules for 25/465/587/993
- [ ] **Preserve evidence:** Archive logs to `docs/08-delivery/poc-evidence/` before cleanup

**NO VPS DESTRUCTION:** Rollback is component-scoped only. The VPS itself will NOT be terminated or reprovisioned.

---

## 5. Verdict: PARTIALLY READY

### What is VERIFIED
- ✅ DNS baseline complete (no conflicts, clean slate)
- ✅ Stalwart v1.1.0 pinned with upgrade caveat
- ✅ Phase 1 PoC plan corrected (mission constraints satisfied)
- ✅ §13 API claims marked NOT VERIFIED
- ✅ RISK-009 added for unverified Management API
- ✅ Jira coverage decision documented (no new items for OPS-001/OPS-004)
- ✅ Approval-gated infrastructure changes listed

### What is NOT VERIFIED
- ❌ **VPS readiness:** SSH unreachable, cannot confirm CPU/RAM/Disk/Docker/ports
- ❌ **Stalwart Management API:** Endpoints/auth/permissions not validated from official docs
- ❌ **Port 25 inbound:** Cannot test without VPS access + firewall approval
- ❌ **DNS configuration:** Records not yet added (approval-gated)

### What is BLOCKED
- 🚫 **Phase 1A execution:** Requires VPS SSH access + infrastructure approval
- 🚫 **Phase 1B execution:** Requires DomiBox application code (not in scope)

### Next Steps (Owner Action Required)
1. **Restore SSH access** to vps-tencent3b (check VPS status, firewall, SSH daemon)
2. **Approve infrastructure changes** (DNS, firewall, VPS deployment)
3. **Execute VPS preflight** (CPU/RAM/Disk/Docker/ports verification)
4. **Authorize Phase 1A PoC** (Stalwart deployment + mail flow testing)
5. **Defer Phase 1B** (lifecycle 7.2/7.3) to Phase 2 (application layer)

---

## 6. Evidence

### DNS Query Raw Responses
See `docs/08-delivery/poc-evidence/dns-baseline-2026-11-16.json` (to be created during PoC execution)

### SSH Connection Log
```
$ ssh -o BatchMode=yes -o ConnectTimeout=20 vps-tencent3b
kex_exchange_identification: read: Connection timed out
banner exchange: Connection to 43.153.206.84 port 22: Connection timed out

Wall time: 19.31 seconds
```

### Jira Sync Map
- DBX-8 (EPIC-07): Security & HTML Sanitization (covers OPS-001/OPS-004 at epic level)
- RTM: Story-level GAP documented for OPS-001/OPS-004

---

**Report Author:** omp-orchestrator  
**Report Date:** 2026-11-16  
**Status:** PARTIALLY READY (DNS verified; VPS preflight BLOCKED)
