# Stalwart vendor verification notes (Phase 1A PoC)

**Verified:** 2026-11-18 against official Stalwart documentation and release pages.
**Rule:** anything not listed here as vendor-confirmed stays `NOT VERIFIED` until a live, authorized PoC tests it.

## Vendor-confirmed facts

| # | Fact | Source | Status |
| --- | --- | --- | --- |
| 1 | Current stable release is **v1.1.1** (released 2026-11-16); v1.1.0 was 2026-11-09, v1.0.3 was 2026-11-04. | https://github.com/stalwartlabs/stalwart/releases | `VERIFIED` |
| 2 | Image is `stalwartlabs/stalwart` (Docker Hub) or `ghcr.io/stalwartlabs/stalwart`. Tags: `v1` (newest 1.x), `v1.1` (newest patch), `v1.1.1` (exact), `-alpine` variant. Avoid `latest`. | https://stalw.art/docs/install/platform/docker , https://stalw.art/docs/install/upgrade | `VERIFIED` |
| 3 | `config.json` contains only the DataStore object, e.g. `{"@type":"RocksDb","path":"/var/lib/stalwart/"}`. All other configuration is stored as objects in the data store. | https://stalw.art/docs/configuration/ | `VERIFIED` |
| 4 | Default listeners after setup: `smtp` 25 (STARTTLS), `submissions` 465, `imaps` 993, `pop3s` 995, `sieve` 4190, `https` 443, `http` 8080. Listener changes require a restart. Unpublished container ports cannot collide with host Caddy. | https://stalw.art/docs/server/listener | `VERIFIED` |
| 5 | First start has no config -> **bootstrap mode**: plain HTTP only on 8080, setup wizard, temporary `admin` password printed in container logs. After submitting the wizard, restart the container to leave bootstrap mode. | https://stalw.art/docs/install/platform/docker | `VERIFIED` |
| 6 | Wizard defaults suit a single server: RocksDB (embedded), internal directory, Console logging for Docker. Setup choices map to the `Bootstrap` object, which can also be submitted via JMAP for automated installs. | https://stalw.art/docs/install/platform/docker | `VERIFIED` |
| 7 | Management interface is the **JMAP API at `/jmap/`** with capabilities `urn:ietf:params:jmap:core` and `urn:stalwart:jmap`. Config objects use `x:<Object>/get` and `x:<Object>/set`. `/api/schema` is a separate read-only schema interface; changes go through `/jmap/`. | https://stalw.art/docs/management/ , https://stalw.art/docs/configuration/ | `VERIFIED` |
| 8 | Management authentication is HTTP Basic (`-u admin@example.com:<password>`) or Bearer token (`API_<key>` / OAuth access token). CLI flags: `STALWART_URL`, `STALWART_USER`, `STALWART_PASSWORD`, `STALWART_TOKEN`. | https://stalw.art/docs/configuration/ , https://stalw.art/docs/management/cli/ | `VERIFIED` |
| 9 | `x:Account/set` creates `{"@type":"User", "name":..., "domainId":..., "credentials":{"0":{"@type":"Password","secret":...}}, "aliases":{"0":{"name":...,"domainId":...}}, "roles":{"@type":"User"}, "permissions":{"@type":"Inherit"}, "quotas":...}`. Aliases are a **field on the Account object**, added/removed with JSON-patch paths such as `aliases/1`. There is no separate `x:Alias/set` object in the current docs. Numeric-indexed lists are JSON **objects**, not arrays. | https://stalw.art/docs/auth/accounts/manage | `VERIFIED` |
| 10 | Standard mail JMAP methods (`Email/query`, `Email/get`, `Mailbox/get`, `Mailbox/set`) are the mail-data interface; these are IETF-standard methods, not invented endpoints. | https://stalw.art/docs/http/jmap/ , ADR-004 | `VERIFIED` (method names); behaviour `NOT EXECUTED` |
| 11 | v1.1.0 added `x:Passkey` objects and passkey permissions to default roles; upgraded v1.0.x servers restart once with `STALWART_UPDATE_ROLE_PERMISSIONS=true`, then remove it. A **fresh** v1.1.1 install does not need it. | https://github.com/stalwartlabs/stalwart/releases/tag/v1.1.0 | `VERIFIED` |
| 12 | v1.1.1 moved **masked email addresses into the open-source edition** ("no longer require an Enterprise license"). This supersedes the old F2 premise in `docs/03-architecture/adr/ADR-002.md` and `ADR-003.md` that masked email is Enterprise-only. | https://github.com/stalwartlabs/stalwart/releases/tag/v1.1.1 | `VERIFIED` |
| 13 | With manual DNS management, ACME uses TLS-ALPN-01 on port 443. Port 443 is occupied by host Caddy; therefore the PoC wizard must use **Manual DNS management** and leave automatic certificate acquisition OFF. A self-signed localhost certificate is expected until TLS is deliberately arranged. | https://stalw.art/docs/install/platform/docker | `VERIFIED` |
| 14 | RocksDB is the embedded default data store; PostgreSQL is optional and only needed for shared/clustered or specifically chosen deployments. | https://stalw.art/docs/install/ , https://stalw.art/docs/install/store/ | `VERIFIED` |

## Corrections to older project assumptions

- `docs/08-delivery/plans/phase1-poc-execution-plan.md` §13 lists `x:Alias/set` as a claimed endpoint. **Corrected:** aliases are patched on `x:Account/set` (`aliases/<n>`); no `x:Alias/set` appears in current official docs. `x:Account/set` itself is confirmed.
- The same §13 claimed management auth was "unverified". **Corrected:** Basic auth and Bearer/API-key auth are documented. The specific credentials for our PoC remain `NOT CREATED` / `REQUIRES OWNER APPROVAL`.
- ADR-002/ADR-003 "Masked Email is Enterprise-only" — **superseded** by v1.1.1 release notes (fact 12 above).
- The PoC plan pins Stalwart v1.1.0; the current stable is v1.1.1. This PoC pins **v1.1.1** and records the pin decision as `REQUIRES OWNER APPROVAL` (ADR-002 still says v1.0.3).

## Explicitly NOT VERIFIED (do not claim otherwise)

- SMTP inbound reachability from the internet (port 25 externally FILTERED at preflight; no active listener; no external test performed).
- STARTTLS negotiation with a real sender, DKIM/SPF/DMARC evaluation, JMAP session against a live server.
- Whether account/alias provisioning succeeds with our exact permissions and domain setup.
- Any functional PASS result. All smoke tests are `NOT EXECUTED`.
