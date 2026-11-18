#!/usr/bin/env bash
# DomiBox Phase 1A - controlled SMTP/JMAP smoke-test DEFINITIONS.
# NOT EXECUTED by default. Running this against the VPS requires a separate,
# explicit owner authorization AND a live, configured Stalwart PoC.
#
#   bash scripts/smoke-test.sh                 # print definitions only (safe)
#   POC_LIVE_AUTHORIZED=yes POC_ADMIN_USER=... POC_ADMIN_PASS=... \
#     bash scripts/smoke-test.sh --authorized  # execute (ONLY with approval)
#
# No credentials are stored in this repository. Supply them via the environment.
# SMTP acceptance / JMAP results remain NOT VERIFIED until an authorized run.
set -u
cd "$(dirname "$0")/.." || exit 1

AUTH=0
[ "${1:-}" = "--authorized" ] && AUTH=1

JMAP_URL="${POC_JMAP_URL:-http://127.0.0.1:8080/jmap/}"
DOMAIN="${POC_TEST_DOMAIN:-sintaksis.biz.id}"
LOCALPART="${POC_TEST_LOCALPART:-poc-smoke-$(date -u +%s)}"
ADMIN_USER="${POC_ADMIN_USER:-}"
ADMIN_PASS="${POC_ADMIN_PASS:-}"

print_definitions() {
  cat <<'DEFS'
SMOKE TEST DEFINITIONS (NOT EXECUTED)
=====================================
Gate 0  Prerequisites (all must hold)
  - Owner authorization recorded; TCP/25 open in Tencent SG + UFW.
  - Stalwart v1.1.1 running as project `domibox-poc`; setup wizard completed;
    container restarted out of bootstrap mode.
  - Admin credentials supplied via environment only (never committed).
  - Throwaway test domain/account only. No real mail accounts.

Gate 1  TCP reachability
  - From an EXTERNAL network: nc -vz <vps-ip> 25  (expect connection + SMTP 220)
  - From the host:  ss -tlnp | grep ':25'  (expect stalwart listener)
  - NOTE: preflight observed port 25 FILTERED externally; this gate is NOT VERIFIED.

Gate 2  SMTP / STARTTLS
  - EHLO -> verify STARTTLS advertised; openssl s_client -starttls smtp -connect 127.0.0.1:25
  - Deliver a test message to the throwaway alias; expect 250 OK and stored message.

Gate 3  JMAP session (vendor-confirmed endpoint /jmap/)
  - GET /jmap/ with Basic auth -> session object; capabilities include
    urn:ietf:params:jmap:core, urn:stalwart:jmap, urn:ietf:params:jmap:mail.

Gate 4  Management API (vendor-confirmed methods)
  - x:Domain/get       -> discover domainId
  - x:Account/set create -> {"@type":"User","name":...,"domainId":...,
      "credentials":{"0":{"@type":"Password","secret":"<throwaway>"}},
      "aliases":{"0":{"name":...,"domainId":...}},"roles":{"@type":"User"},
      "permissions":{"@type":"Inherit"}}
  - x:Account/set update patch "aliases/1" -> add/disable/remove alias
  - x:Account/set destroy -> delete throwaway account
  - There is NO x:Alias/set object; aliases are patched on x:Account/set.

Gate 5  Mail data (standard JMAP methods)
  - Email/query (accountId from created account) -> message ids
  - Email/get  -> subject/headers/raw source of the delivered test message
  - Mailbox/get -> INBOX id (read-only folder listing)

Gate 6  Cleanup
  - Destroy the throwaway account; confirm no production accounts touched.
  - Record outputs under docs/08-delivery/poc-evidence/ (never commit secrets).

RESULT UNTIL AN AUTHORIZED RUN: all gates NOT EXECUTED / NOT VERIFIED.
DEFS
}

jmap() {
  # $1 = JSON-RPC methodCalls payload body (without using/outer envelope added here)
  curl -sS -u "$ADMIN_USER:$ADMIN_PASS" -H 'Content-Type: application/json' \
    -X POST "$JMAP_URL" \
    -d "{\"using\":[\"urn:ietf:params:jmap:core\",\"urn:stalwart:jmap\",\"urn:ietf:params:jmap:mail\"],\"methodCalls\":[$1]}" 2>/dev/null
}

authorized_run() {
  echo "=== AUTHORIZED SMOKE RUN (throwaway account only) ==="
  [ "$AUTH" -eq 1 ] || { echo "Refusing: --authorized not passed"; exit 2; }
  [ "${POC_LIVE_AUTHORIZED:-}" = "yes" ] || { echo "Refusing: POC_LIVE_AUTHORIZED != yes"; exit 2; }
  [ -n "$ADMIN_USER" ] && [ -n "$ADMIN_PASS" ] || { echo "Refusing: admin credentials not supplied via environment"; exit 2; }

  echo "[Gate 3] JMAP session:"
  curl -sS -u "$ADMIN_USER:$ADMIN_PASS" "$JMAP_URL" 2>/dev/null | python -m json.tool 2>/dev/null || echo "  session request failed"

  echo "[Gate 4] Domain discovery:"
  jmap '["x:Domain/get",{},"d1"]' | python -m json.tool 2>/dev/null || echo "  domain query failed"

  echo "[Gate 4] Create throwaway account with alias:"
  jmap "[\"x:Account/set\",{\"create\":{\"t1\":{\"@type\":\"User\",\"name\":\"${LOCALPART}\",\"domainId\":\"REPLACE_WITH_DOMAIN_ID\",\"aliases\":{\"0\":{\"name\":\"${LOCALPART}\",\"domainId\":\"REPLACE_WITH_DOMAIN_ID\"}},\"roles\":{\"@type\":\"User\"},\"permissions\":{\"@type\":\"Inherit\"}}}},\"c1\"]" | python -m json.tool 2>/dev/null || echo "  account create failed"

  echo "[Gate 1/2] SMTP send (requires swaks or python smtplib against 127.0.0.1:25):"
  if command -v swaks >/dev/null 2>&1; then
    swaks --to "${LOCALPART}@${DOMAIN}" --from "poc-sender@example.invalid" \
      --server 127.0.0.1 --port 25 --tls --header "Subject: DomiBox PoC smoke test" \
      --body "Throwaway PoC message - discard" || echo "  swaks delivery failed"
  else
    echo "  swaks unavailable - use python smtplib with STARTTLS (see README)"
  fi

  echo "[Gate 5] Email/query + Email/get (fill accountId from create response):"
  jmap '["Email/query",{"accountId":"REPLACE_WITH_ACCOUNT_ID","limit":5},"e1"]' | python -m json.tool 2>/dev/null || echo "  Email/query failed"

  echo "[Gate 6] Destroy throwaway account (fill id):"
  echo "  x:Account/set destroy { ids: [\"REPLACE_WITH_ACCOUNT_ID\"] }"
  echo
  echo "Authorized run complete. Evaluate each gate manually; do not claim PASS without evidence."
}

if [ "$AUTH" -eq 1 ]; then
  authorized_run
else
  print_definitions
fi
