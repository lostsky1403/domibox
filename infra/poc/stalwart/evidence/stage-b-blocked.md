# Stage B — baseline and Gate 1 blocker

**Date:** 2026-11-18 (UTC) · **Verdict: STAGE B BLOCKED** at Gate 1 (inbound SMTP eligibility).
**No Stage B change was applied.** No Security Group, UFW, DNS, Compose binding, container state or unrelated service was modified.

## Gate 0 — baseline (executed, read-only)

| Item | Observed |
| --- | --- |
| Git worktree | `F:\DomiBox-worktrees\phase1a-stalwart-poc`, branch `feat/phase1a-stalwart-poc`, HEAD `d834c11da0ef8d64a190fb7fe494f98b2fe43acd`, clean, matches `origin/feat/phase1a-stalwart-poc` |
| PRs | #2 open/draft, head `feat/phase1a-stalwart-poc`, base `docs/project-bootstrap`, contains Stage A fixes; #1 unchanged |
| Docker context | `default`, `unix:///var/run/docker.sock` on the VPS; Docker 29.9.3 / Compose v5.7.0 |
| PoC container | `domibox-poc-stalwart`, `Exited (0)`, image `stalwartlabs/stalwart:v1.1.1` |
| PoC volumes / network | `domibox-poc_etc`, `domibox-poc_data`, `domibox-poc_net` — preserved |
| CPU / memory / disk | 2 vCPU; 2.2 GiB available; 47 GB free (18%); inode use 8% |
| Host listeners | `127.0.0.1:9000-9001` (rustfs), `*:80`, `*:443` (Caddy). Ports 25 and 8080 free |
| Caddy | `active`, PID 1950550, config `/etc/caddy/Caddyfile` |
| Other workload | `rustfs` Up 7 days on `127.0.0.1:9000-9001`; no n8n container observed |
| UFW (authenticated read) | enabled, default `deny (incoming)`; only `22/tcp`, `80/tcp`, `443/tcp` allowed (plus v6). **No 25/tcp rule** |
| Tencent instance metadata | `ins-f6b2sjfy`, region `ap-singapore`, public IP `43.153.206.84` |
| Authoritative DNS (DoH) | MX none; apex A/TXT none; `mail.sintaksis.biz.id` A/AAAA/CNAME NXDOMAIN; NS `dylan`/`kristina.ns.cloudflare.com`; DMARC NXDOMAIN. No Email Routing MX |
| Cloudflare zone | `sintaksis.biz.id`, zone ID `68d70b557d8adba43bb16d00ae1a42c8`, status active, Cloudflare DNS Only nameservers |
| Independent client network | OpenChamber Windows host: TCP 22/80/443 to `43.153.206.84` OPEN; **TCP 25 FILTERED/TIMEOUT** from this client network (egress restriction, not evidence of server state) |

## Gate 1 — why it is BLOCKED

1. `tccli` is not installed on the VPS and neither provider console was authenticated.
2. Tencent Cloud credentials were supplied through the secure secret mechanism and verified to authenticate (`DescribeRegions` returned 19 regions).
3. The same credentials returned **zero** CVM instances for `ins-f6b2sjfy` and **zero** Security Groups in `ap-singapore`, and zero Security Groups in `ap-jakarta`, `ap-hongkong`, `ap-bangkok` and `ap-tokyo`.
4. Therefore the Security Group attached to `ins-f6b2sjfy` cannot be identified, and it is impossible to prove that any inbound TCP/25 rule would be narrowly scoped to this VPS rather than another workload.

Authorized instruction §5 says: *"If the agent cannot safely identify the correct security group or the rule is controlled by another workload, STOP at this gate."* This condition is met, so no Security Group, UFW or DNS change was attempted.

## Gate status

| Gate | Status |
| --- | --- |
| Gate 0 — baseline | **PASS** (read-only evidence captured) |
| Gate 1 — inbound SMTP eligibility | **BLOCKED** (target Security Group not identifiable with supplied credentials) |
| Gate 2 — public SMTP listener | **NOT EXECUTED** |
| Gate 3 — independent public port-25 test | **NOT EXECUTED** (client network also blocks outbound 25; no independent source used) |
| Gate 4 — Cloudflare A/MX | **NOT EXECUTED** (no records created; DNS unchanged) |
| Gate 5 — real external delivery | **NOT EXECUTED** |
| Gate 6 — limited robustness | **NOT EXECUTED** |

## What is needed to resume Stage B

1. Tencent Cloud API credentials (or console access) whose principal can see `ins-f6b2sjfy` and its attached Security Group, so a single inbound TCP/25 rule can be identified, added and later reverted by ID.
2. Confirmation that the supplied Cloudflare token may be used for DNS edits on zone `68d70b557d8adba43bb16d00ae1a42c8` (it authenticated successfully for zone read).
3. An independent external test source with outbound TCP/25 available (the OpenChamber Windows network does not provide one). A third-party SMTP testing service or another authorized network must supply the public greeting and delivery evidence.

## End state (unchanged)

PoC container stopped with exit 0; volumes preserved; Caddy and rustfs healthy; UFW limited to 22/80/443; Cloudflare DNS unchanged; no public SMTP listener; no credentials, tokens or secret file paths committed.
