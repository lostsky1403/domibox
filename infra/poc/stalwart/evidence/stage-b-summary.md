# Stage B — controlled public SMTP inbound test (PARTIAL)

**Date:** 2026-11-19 UTC · **Verdict: STAGE B PARTIAL** — public SMTP reachability, TLS capability, relay protection, DNS publication and reversible cleanup are verified against the real provider APIs; **real external message delivery was not executed** because no available independent source could originate a message to a custom recipient.

## Credential reconciliation (root cause of the earlier blocker)

- The previously supplied Tencent credentials were correct. The earlier `WRONG_ACCOUNT` conclusion was **wrong**: the target is a **Lighthouse** instance, not a CVM.
- VPS metadata: `ins-f6b2sjfy`, `ap-singapore`, `43.153.206.84`, internal `10.3.0.4`, name `lh-1526089049-lhins-owo5m7sf`.
- The instance name contains AppId `1526089049`, matching `CAM GetUserAppId` from the authenticated root principal — account ownership confirmed.
- Lighthouse API (`lh.intl.tencentcloudapi.com`, also `lh.tencentcloudapi.com`) returned `lhins-owo5m7sf` with public IP `43.153.206.84`. CVM `DescribeInstances` returned zero solely because of the product mismatch.
- The Cloudflare token actually used was the saved secure record, distinct from the invalid `API_TOKEN` environment value. Zone read and DNS read returned HTTP 200; `/user/tokens/verify` returned HTTP 401 / code 1000 because that endpoint is user-scoped while this token is zone-scoped. DNS write was subsequently proven by the approved create/delete calls, not assumed.
- No new credentials were generated; no browser login was used; no secret value or full credential path is recorded here.

## Verified gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Target identity | PASS | Lighthouse `lhins-owo5m7sf`, public IP `43.153.206.84`, `ap-singapore` |
| Firewall scope | PASS | Four instance-scoped rules (22/80/443/ICMP); no unrelated instance attached |
| TCP/25 change | PASS / reverted | Lighthouse add `06112241-df99-44ec-ada6-b40574571efa`, delete `8f25baba-d5bb-4b62-80a9-d79834ca79f0`; UFW rule added then deleted |
| Public listener | PASS | `0.0.0.0:25->25`, management `127.0.0.1:8080` only; container 443 not published |
| Independent SMTP test | PASS | MXToolbox US-East connected in 0.581 s; banner `220 mail.sintaksis.biz.id Stalwart ESMTP at your service`; EHLO advertised STARTTLS, SMTPUTF8, SIZE, REQUIRTLS |
| TLS | PASS (capability) | MXToolbox: `SMTP TLS OK - Supports TLS`; certificate verification not performed for the self-signed PoC |
| Relay abuse | PASS | `RCPT TO:<test@mxtoolboxsmtpdiag.com>` → `550 5.7.1 Relay not allowed` |
| DNS | PASS / reverted | A `fda87b27e4a14cead2cf826fe1782b0c`, MX `b2df77b784ec21125d762e2bc3f8dc0e` (DNS Only, TTL 60); authoritative DoH confirmed `mail -> 43.153.206.84` and `MX 10 mail`; both records deleted, zone now empty |
| Disposable identity | PASS | account `d` created and destroyed by exact id; zero `stageb-` accounts remain |
| Real external delivery | **NOT EXECUTED** | Windows and hosted browser both block outbound TCP/25; Wormly sending is subscriber-only; FormSubmit timed out; MXToolbox cannot address a custom recipient |

## Final state

- Lighthouse firewall back to 22/80/443/ICMP only; UFW back to 22/80/443 only; SSH verified after each change.
- Cloudflare zone has zero DNS records; authoritative DoH confirms no MX and no `mail` A.
- Compose binding restored to `127.0.0.1:25`; PoC container stopped (exit 143 via SIGTERM); volumes `domibox-poc_etc` and `domibox-poc_data` preserved; no `down -v`.
- Caddy `active` on 80/443; rustfs Up 8 days on 9000-9001; no n8n container present; no unrelated service changed.
- Machine-readable detail: `stage-b-partial-report.json`.

## Remaining blocker for full Stage B PASS

An independent origin that can actually deliver a message to the disposable recipient is still required: a provider/network with outbound TCP/25, or an external mail service that can send to a custom address. Public reachability itself is already proven; this last item is delivery-and-retrieval evidence only.
