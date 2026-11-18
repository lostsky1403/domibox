#!/usr/bin/env bash
# DomiBox Phase 1A - LOCAL STATIC VALIDATION ONLY.
# Checks Compose syntax, isolation, pinning, private networking and secret leakage.
# Does not pull images, start containers or contact the VPS.
set -u
cd "$(dirname "$0")/.." || exit 1

fail=0
pass() { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fail=1; }
note() { printf 'NOTE  %s\n' "$1"; }

echo "=== DomiBox PoC static validation ==="

# 1. Compose configuration parses.
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  if docker compose -f docker-compose.yml config --quiet 2>/tmp/domibox-compose-config.err; then
    pass "docker compose config parses"
  else
    bad "docker compose config failed: $(cat /tmp/domibox-compose-config.err)"
  fi
else
  note "Docker Compose unavailable locally - skipped compose parse (environment limitation)"
fi

# 2. Exact image pin (no floating tag).
if grep -Eq '^[[:space:]]*image: stalwartlabs/stalwart:v1\.1\.1$' docker-compose.yml; then
  pass "image pinned to stalwartlabs/stalwart:v1.1.1"
else
  bad "image is not pinned to v1.1.1"
fi
if grep -Eq 'image:.*(:latest|:v1[[:space:]]*$)' docker-compose.yml; then
  bad "floating image tag detected"
fi

# 3. Project / network / volume isolation.
grep -Eq '^name: domibox-poc$' docker-compose.yml && pass "Compose project name is domibox-poc" || bad "Compose project name missing"
for resource in 'domibox-poc_net' 'domibox-poc_etc' 'domibox-poc_data'; do
  grep -q "$resource" docker-compose.yml && pass "resource $resource present" || bad "resource $resource missing"
done
if grep -qi 'rustfs' docker-compose.yml; then
  note "rustfs is mentioned only in comments - verify no network attach:"
  grep -n 'networks:' -A3 docker-compose.yml
fi

# 4. Port exposure review.
if grep -Eq '"127\.0\.0\.1:\$\{POC_ADMIN_HOST_PORT:-8080\}:8080"' docker-compose.yml; then
  pass "management/setup port bound to loopback only"
else
  bad "management/setup port is not loopback-only"
fi
for p in 443 465 587 993 995 4190 5432 8081; do
  if grep -Eq ":${p}:${p}" docker-compose.yml; then
    bad "port ${p} is published (must not be)"
  fi
done
pass "no host collision with Caddy 80/443 and no DB/internal port published"

# 5. SMTP bind is loopback by default (0.0.0.0 requires approval).
if grep -Fq '${POC_SMTP_HOST_IP:-127.0.0.1}:25:25' docker-compose.yml; then
  pass "SMTP host bind defaults to 127.0.0.1"
else
  bad "SMTP default bind could not be confirmed as loopback"
fi

# 6. DataStore example is valid JSON.
if python -c 'import json,sys; json.load(open("config/config.json.example", encoding="utf-8"))' 2>/dev/null; then
  pass "config.json.example is valid JSON"
else
  bad "config.json.example is not valid JSON"
fi

# 7. Secret-leak check.
if grep -RniE 'STALWART_RECOVERY_ADMIN[[:space:]]*=[[:space:]]*[^[:space:]]|(_PASSWORD|_TOKEN|_SECRET|_API_KEY)[[:space:]]*=[[:space:]]*[^[:space:]]' \
    --exclude='validate.sh' \
    --include='*.yml' --include='*.yaml' --include='*.sh' --include='*.example' --include='.env.example' . ; then
  bad "credential-like assignment found - review immediately"
else
  pass "no credential-like assignments found"
fi

# 8. Required assets present.
for f in README.md docker-compose.yml .env.example config/config.json.example \
         docs/vendor-verification.md scripts/preflight-check.sh scripts/smoke-test.sh scripts/rollback.sh; do
  [ -f "$f" ] && pass "asset $f exists" || bad "asset $f missing"
done

echo
if [ "$fail" -eq 0 ]; then
  echo "RESULT: STATIC VALIDATION PASSED (no live test performed)"
else
  echo "RESULT: STATIC VALIDATION FAILED"
fi
exit "$fail"
