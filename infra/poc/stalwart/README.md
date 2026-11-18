# DomiBox Phase 1A — Isolated Stalwart PoC preparation

**Status:** `PROPOSED` — local artifacts prepared and statically validated. **No live deployment, no VPS/DNS/firewall changes.**
**Branch:** `feat/phase1a-stalwart-poc` (based on `origin/docs/project-bootstrap` @ `c97a8e4`; stacked PR planned, base `docs/project-bootstrap`).
**Verified against vendor docs:** 2026-11-18 — see `docs/vendor-verification.md`.

---

## 1. Purpose and safety boundary

These files prepare the **minimum executable assets** for a controlled Stalwart mail-engine PoC on `vps-tencent3b`. They are **local-only**. Running them, pulling the image, opening port 25, or touching DNS/firewall/Caddy requires a separate, explicitly authorized task.

Never done by this repo or its scripts:

- Deploying or starting Stalwart on the VPS.
- Changing UFW, Tencent Security Groups or Cloudflare DNS.
- Editing/restarting host Caddy (systemd service, v2.11.9) on host ports 80/443.
- Touching the unrelated `rustfs` container, its volumes or `rustfs_default` network.
- Creating production mail accounts or committing credentials.
- `docker compose down -v` without owner approval and an ownership check.

The PoC is **component-scoped and independently reversible**: Compose project `domibox-poc`, network `domibox-poc_net`, volumes `domibox-poc_etc` and `domibox-poc_data`, container `domibox-poc-stalwart`.

---

## 2. Vendor-confirmed facts driving this design

| Decision | Vendor evidence | Result here |
| --- | --- | --- |
| Image | `stalwartlabs/stalwart` tags `v1`, `v1.1`, `v1.1.1`; avoid `latest` | Pin **`stalwartlabs/stalwart:v1.1.1`** (current stable, 2026-11-16) |
| Data store | `config.json` holds only the DataStore object; default is embedded RocksDB | RocksDB in `domibox-poc_data`; **no PostgreSQL** for Phase 1A |
| Config model | Everything else is a JMAP object at `/jmap/`; `/api/schema` is read-only | All provisioning via JMAP management API |
| Listeners | Defaults: 25, 465, 993, 995, 4190, 443, 8080; bound inside container | Publish **only** 25 (loopback default) and 127.0.0.1:8080 |
| Bootstrap | First start = wizard on plain HTTP 8080; temp `admin` password in logs; restart after wizard | 8080 published on loopback, reached via SSH tunnel |
| Management auth | HTTP Basic or Bearer API key (`API_<key>`) | Credentials supplied via environment at run time, never committed |
| Aliases | Aliases are a field on `x:Account/set` (`aliases/<n>`); **no `x:Alias/set`** | Use `x:Account/set` create/patch/destroy for alias lifecycle |
| TLS/ACME | Manual DNS management uses TLS-ALPN-01 on 443 | Wizard must use **Manual DNS management**, auto-certificate OFF; self-signed cert expected |
| v1.1.1 change | Masked email is now open source | Supersedes ADR-002/003 "Enterprise-only" premise |

**Not verified until a live authorized run:** SMTP acceptance, STARTTLS negotiation, JMAP session against a live server, alias CRUD, message storage/retrieval, DNS authentication, and external reachability of port 25.

---

## 3. File map

| File | Function |
| --- | --- |
| `docker-compose.yml` | Isolated `domibox-poc` project: exact image pin, 25 + loopback 8080 only, dedicated volumes/network/labels, no Caddy/rustfs references. |
| `.env.example` | No-credential template for host bind, admin port and restart policy. Copy locally; never commit `.env`. |
| `config/config.json.example` | Reference minimal RocksDB DataStore object (`{"@type":"RocksDb","path":"/var/lib/stalwart/"}`). The wizard writes the real file into the volume. |
| `docs/vendor-verification.md` | Vendor facts with source URLs, corrections to older project assumptions, explicit NOT VERIFIED list. |
| `scripts/preflight-check.sh` | Read-only prerequisite check (CPU/RAM/disk/inode, ports, Docker, UFW-with-`sudo -n`, existing workloads). Never changes anything. |
| `scripts/validate.sh` | Local static validation: Compose parse, exact pin, isolation, loopback bind, no secret leakage, JSON validity. |
| `scripts/smoke-test.sh` | Guarded SMTP/JMAP smoke-test **definitions**; executes only with `--authorized` + `POC_LIVE_AUTHORIZED=yes` + env credentials. |
| `scripts/rollback.sh` | Component-scoped stop (reversible) or `down -v` with ownership check + typed confirmation. |

---

## 4. Deployment design (for the later authorized run only)

1. **No host port collision.** Caddy owns host 80/443; the Compose file never publishes them. The container's internal 443 listener is harmless because it is in the container network namespace.
2. **Private management.** Setup wizard and JMAP/admin are published only on `127.0.0.1:8080`. Access from the workstation via `ssh -L 8080:127.0.0.1:8080 vps-tencent3b`. Never expose this on `0.0.0.0`.
3. **SMTP listener.** Port 25 published on loopback by default (`POC_SMTP_HOST_IP=127.0.0.1`). Setting it to `0.0.0.0` is `REQUIRES OWNER APPROVAL` and must follow Tencent SG + UFW changes.
4. **Dedicated resources.** Project/network/volumes/container are all named `domibox-poc*`. Never join `rustfs_default` or any shared network.
5. **RocksDB, no PostgreSQL.** Adequate for single-node PoC; ~2.3 GiB RAM and 48 GB disk are available on the host.
6. **Manual DNS, no ACME automation.** The wizard must select Manual DNS management and disable automatic certificate acquisition, because port 443 is Caddy's and no DNS records are authorized. Expect a self-signed `localhost` certificate until TLS is deliberately arranged.
7. **Rollback independence.** Stop is reversible; data destruction needs an explicit ownership check and owner approval. No shared resource is touched.

### Temporary-alias structure decision

Stalwart 1.1.x stores aliases **on the Account object** (`aliases/<n>`), so the ADR-003 model — one internal ingestion account with aliases patched onto it — is directly implementable. The PoC will use that model as the primary experiment. A dedicated mailbox per alias (proposed in the 2026-11-18 preflight as gate 6) is retained as a comparison case only; no production structure is chosen until the owner decides.

---

## 5. Initialization runbook (NOT executed here)

Executing any of this requires owner authorization recorded first.

1. Confirm approvals in §7 and run `bash scripts/preflight-check.sh` over SSH; resolve every `REVIEW` line that is an actual blocker.
2. Copy `.env.example` to `.env` locally; keep `POC_SMTP_HOST_IP=127.0.0.1` until approved.
3. `docker compose -f docker-compose.yml config` and `bash scripts/validate.sh` locally.
4. `docker compose -f docker-compose.yml -p domibox-poc up -d` on the VPS (authorized run only).
5. In another terminal: `ssh -L 8080:127.0.0.1:8080 vps-tencent3b`.
6. Open `http://127.0.0.1:8080/admin`; read the temporary `admin` password from `docker logs domibox-poc-stalwart 2>&1 | grep -A8 'bootstrap mode'`.
7. Complete the wizard: hostname `mail.sintaksis.biz.id` (or approved PoC host), default domain `sintaksis.biz.id`, **RocksDB default**, **internal directory**, **Console logging**, **Manual DNS management**, automatic certificate OFF. Record the generated administrator address + password securely; do not commit it.
8. Restart the container: `docker compose -f docker-compose.yml -p domibox-poc restart stalwart`.
9. Run the guarded smoke tests (§6). Capture evidence under `docs/08-delivery/poc-evidence/` in a later, authorized commit; redact secrets.
10. Stop with `bash scripts/rollback.sh stop`. Destroy only after approval via `bash scripts/rollback.sh --destroy-data`.

---

## 6. Validation status

**Performed locally (2026-11-18):**

- `docker compose version` → v2.38.2-desktop.1 available.
- `docker compose -f docker-compose.yml config --quiet` → parses (see commit validation log).
- `bash scripts/validate.sh` → static checks: pin, isolation, loopback binding, port-collision review, JSON validity, secret-leak scan.
- `bash scripts/preflight-check.sh` syntax reviewed; intended for the target host, not run against live infrastructure in this task.

**Not performed:** image pull, container start, SMTP/JMAP functional tests, external port-25 test, DNS changes. All live capabilities remain `NOT VERIFIED` / `NOT EXECUTED`.

---

## 7. Exact changes requiring owner approval before live PoC

1. **Docker image / version:** accept the v1.1.1 pin (ADR-002 still says v1.0.3; PoC plan says v1.1.0).
2. **Tencent Security Group:** add inbound TCP/25 for `ins-f6b2sjfy`.
3. **UFW:** allow `25/tcp` (currently not allowed per owner evidence).
4. **Cloudflare DNS:** A `mail.sintaksis.biz.id` → `43.153.206.84`, MX → mail (10), SPF, DMARC, DKIM from Stalwart — DNS Only (grey cloud). **Not changed in this task.**
5. **Host bind:** set `POC_SMTP_HOST_IP=0.0.0.0` only after 2–4 are done.
6. **Throwaway credentials / domain:** authorize creation of PoC-only admin + test account.
7. **Caddy:** no change is planned; any reverse-proxy stanza for Stalwart HTTPS/JMAP is a separate, approval-gated change.
8. **Data destruction:** required only at teardown, with ownership check and explicit approval.

**Go/No-Go:** local preparation is complete; live PoC is **NO-GO until 1–6 are approved and executed in a separate authorized task**.

---

## 8. References

- Official install/Docker: https://stalw.art/docs/install/platform/docker/
- Configuration model: https://stalw.art/docs/configuration/
- Listeners: https://stalw.art/docs/server/listener
- Management API: https://stalw.art/docs/management/
- Accounts/aliases: https://stalw.art/docs/auth/accounts/manage
- CLI: https://stalw.art/docs/management/cli/
- Releases/tags: https://github.com/stalwartlabs/stalwart/releases , https://stalw.art/docs/install/upgrade
- Project docs: `docs/08-delivery/phase1-preflight-report.md`, `docs/08-delivery/plans/phase1-poc-execution-plan.md`, `docs/03-architecture/diagrams/network-port-matrix.md`, `docs/03-architecture/adr/ADR-002.md`, `ADR-003.md`, `ADR-004.md`
