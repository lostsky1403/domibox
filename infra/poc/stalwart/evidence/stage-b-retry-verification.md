# Stage B retry verification — TGB-20261119T1800Z

**Result: STAGE B NOT PASSED — Gmail SENT but no delivery evidence.**

## Test setup (verified live)

- Recipient: `stageb-0f3f798136@sintaksis.biz.id` (JMAP account id `f`), created via private JMAP.
- Subject token: `DOMIBOX-RETRY-63FF9052`.
- Authoritative DoH: `MX 10 mail.sintaksis.biz.id.` and `A mail.sintaksis.biz.id -> 43.153.206.84`.
- Public SMTP: MXToolbox US-East greeting `220 mail.sintaksis.biz.id Stalwart ESMTP at your service`.
- Recipient eligibility: `MAIL FROM` → `250 2.1.0 OK`, `RCPT TO` → `250 2.1.5 OK`.
- Window: ready 18:02 UTC, scheduled expiry 18:20 UTC (task `25fbd9e4-197d-4df0-9b18-ae975de48f91`, `nextRunAt` verified as 18:20:00 UTC).

## Observation

Owner supplied Gmail API confirmation: message id `1a1f501e01a31f20`, status SENT, send time ~18:11 UTC.

| Check | Result |
| --- | --- |
| JMAP `Email/query` for account `f` | `ids: []` on every poll; 30 bounded polls over 90 seconds, subject+recipient never matched |
| JMAP `Email/get` | No message retrieved |
| Stalwart SMTP logs from 18:05 onward | No Gmail connection, no `DATA`, no message-id or subject/recipient match |
| SMTP `RCPT` log | Only the agent's own eligibility probe at 18:01:56; no provider transaction |
| Gmail SENT | Provider-side submission only; no Stalwart acceptance, mailbox delivery or JMAP visibility |

**Conclusion:** the Gmail API reported SENT, but no message reached the Stalwart listener or mailbox. STAGE B PASS requires JMAP retrieval, which did not occur. No mail-engine defect is proven; the delivery did not complete.

## Exact-ID cleanup (completed 18:23 UTC)

| Resource | Action |
| --- | --- |
| Cloudflare A `60b9042abf0f35d3ff1e6d545191a394` | Deleted via Cloudflare MCP; zone now 0 records |
| Cloudflare MX `2fe72343fbd0b741a748474bee0525bd` | Deleted via Cloudflare MCP |
| Lighthouse TCP/25 rule `domibox-stage-b-retry-TGB1800`, instance `lhins-owo5m7sf` | Deleted (request `101b5d30-2e99-4d6d-a0d4-44ca2c92a661`); only 22/80/443/ICMP remain |
| UFW `25/tcp` comment `domibox-stage-b-retry-TGB1800` | Deleted; 22/80/443 unchanged |
| JMAP account `f` | Verified name `stageb-0f3f798136`, destroyed by exact id, follow-up get returned `notFound` |
| Compose binding | Restored `POC_SMTP_HOST_IP=127.0.0.1`; container recreated then stopped (`Exited (143)`) |
| Volumes | `domibox-poc_etc`, `domibox-poc_data` preserved; no `down -v` |
| Scheduled task | Disabled after manual cleanup |

Final verification: no port 25 or 8080 listener; Caddy `active` on 80/443; rustfs Up 9 days on 9000-9001; SSH reachable; DNS empty. No credentials, tokens or secret paths recorded.
