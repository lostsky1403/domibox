#!/usr/bin/env bash
# DomiBox Phase 1A - PoC test dispatcher.
#
# Default (no arguments): STATIC / DRY RUN. No network calls, no Docker, no DNS,
# no account creation. Produces a structured report with NOT_EXECUTED tests.
#
#   bash scripts/smoke-test.sh                              # static (safe)
#   bash scripts/smoke-test.sh --mode local \
#       --local-authorized --confirm-local LOCAL-POC        # local functional
#   bash scripts/smoke-test.sh --mode external \
#       --external-smtp-host <public-ip> \
#       --external-authorized --confirm-external <public-ip> # external inbound
#
# Credentials come from POC_ADMIN_USER / POC_ADMIN_PASS / POC_ADMIN_TOKEN and
# are never printed or stored. See README.md for the full mode contract.
set -u
cd "$(dirname "$0")/.." || exit 1

PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
if [ -z "$PY" ]; then
  echo "ERROR: python3 is required for the PoC test runner" >&2
  exit 2
fi

exec "$PY" scripts/poc_runner.py "$@"
