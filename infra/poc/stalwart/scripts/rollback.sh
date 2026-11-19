#!/usr/bin/env bash
# DomiBox Phase 1A - component-scoped rollback.
# SAFE DEFAULT: prints the plan. `stop` is reversible; `down -v` is destructive
# and requires explicit owner approval plus a typed confirmation.
# This script NEVER touches Caddy, rustfs, other containers, shared volumes or DNS.
set -u
cd "$(dirname "$0")/.." || exit 1

PROJECT="domibox-poc"
COMPOSE="docker compose -f docker-compose.yml -p ${PROJECT}"

echo "=== DomiBox PoC rollback (component-scoped) ==="
echo "Project: ${PROJECT}   Compose file: $(pwd)/docker-compose.yml"

echo
echo "--- Resources that belong to this PoC (verify before any destructive step) ---"
${COMPOSE} ps 2>/dev/null || echo "  (compose project not running or docker unavailable)"
echo "Volumes matching ${PROJECT}:"
docker volume ls --filter "name=${PROJECT}" 2>/dev/null || echo "  (docker unavailable)"
echo "Networks matching ${PROJECT}:"
docker network ls --filter "name=${PROJECT}" 2>/dev/null || echo "  (docker unavailable)"

action="${1:-print}"
case "$action" in
  print)
    cat <<'PLAN'
REVERSIBLE (no data loss, no owner approval needed):
  docker compose -f docker-compose.yml -p domibox-poc stop
DESTRUCTIVE (REQUIRES owner approval + typed confirmation):
  1. Verify `docker volume ls --filter name=domibox-poc` lists ONLY domibox-poc_* volumes.
  2. Archive evidence/logs first.
  3. POC_DATA_DESTROY_APPROVED=yes bash scripts/rollback.sh --destroy-data
     then type: DESTROY-DOMIBOX-POC-DATA
NEVER RUN:
  - docker compose down -v on any other project
  - commands that remove Caddy, rustfs, shared volumes or networks
  - any Cloudflare DNS, UFW or Security Group change as "rollback"
PLAN
    ;;
  stop)
    echo "Stopping ${PROJECT} containers (data preserved)..."
    ${COMPOSE} stop
    echo "Stopped. Volumes and configuration are intact; restart with: ${COMPOSE} start"
    ;;
  --destroy-data)
    [ "${POC_DATA_DESTROY_APPROVED:-}" = "yes" ] || {
      echo "REFUSED: owner data-destruction approval (POC_DATA_DESTROY_APPROVED=yes) is missing"; exit 2; }
    vol_list=$(docker volume ls -q --filter "name=${PROJECT}" 2>/dev/null || true)
    echo "Volumes to be deleted:"
    echo "$vol_list"
    for v in $vol_list; do
      case "$v" in
        domibox-poc_*) ;;
        *) echo "REFUSED: unexpected volume '$v' matched the filter"; exit 2 ;;
      esac
    done
    printf 'Type DESTROY-DOMIBOX-POC-DATA to proceed: '
    read -r confirm
    [ "$confirm" = "DESTROY-DOMIBOX-POC-DATA" ] || { echo "REFUSED: confirmation mismatch"; exit 2; }
    echo "Running component-scoped destruction for ${PROJECT} only..."
    ${COMPOSE} down -v
    echo "Done. Verify with: docker volume ls --filter name=${PROJECT}"
    ;;
  *)
    echo "Unknown action '$action'. Use: print | stop | --destroy-data"; exit 2
    ;;
esac
