#!/usr/bin/env bash
# DomiBox Phase 1A - READ-ONLY prerequisite check.
# Safe to run locally or over SSH on vps-tencent3b. It NEVER changes anything:
# no writes, no sudo prompts (sudo -n only), no container/network/firewall changes.
#
# Usage:  bash scripts/preflight-check.sh
#         ssh vps-tencent3b 'bash -s' < scripts/preflight-check.sh
set -u

echo "=== DomiBox Phase 1A preflight (READ-ONLY) ==="
echo "Run at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

section() { printf '\n--- %s ---\n' "$1"; }
review()  { printf 'REVIEW: %s\n' "$1"; }
ok()      { printf 'OK: %s\n' "$1"; }

section "Identity / kernel"
uname -a || review "uname failed"
date -u +'%Y-%m-%dT%H:%M:%SZ'
timedatectl status 2>/dev/null | grep -E 'Time zone|System clock synchronized' || review "timedatectl unavailable"

section "CPU / memory / swap"
printf 'vCPU: '; nproc 2>/dev/null || review "nproc failed"
free -h 2>/dev/null || review "free failed"
[ -r /proc/swaps ] && cat /proc/swaps || review "swap info unavailable"

section "Disk / inodes"
df -h / 2>/dev/null || review "df failed"
df -i / 2>/dev/null || review "inode check failed"

section "Docker / Compose"
if docker --version 2>/dev/null; then ok "Docker present"; else review "Docker missing"; fi
if docker compose version 2>/dev/null; then ok "Compose plugin present"; else review "Compose plugin missing"; fi
docker info --format 'Server={{.ServerVersion}} Running={{.ContainersRunning}} Driver={{.Driver}}' 2>/dev/null || review "docker info unavailable"

section "Listening ports (port-collision review)"
ss -tlnp 2>/dev/null || review "ss unavailable"
for p in 25 80 443 8080 2019 9000 9001; do
  if ss -tln 2>/dev/null | awk '{print $4}' | grep -Eq "(:|\\])${p}$"; then
    printf 'PORT %s: occupied\n' "$p"
  else
    printf 'PORT %s: free\n' "$p"
  fi
done
if ss -tln 2>/dev/null | awk '{print $4}' | grep -Eq ':25$'; then
  review "TCP/25 already has a listener - STOP, do not deploy"
else
  ok "TCP/25 has no host listener (expected at preflight)"
fi

section "Firewall (read-only)"
if ufw status verbose 2>/dev/null; then
  ok "UFW rules read without sudo"
elif sudo -n ufw status verbose 2>/dev/null; then
  ok "UFW rules read with passwordless sudo"
else
  if [ -r /etc/ufw/ufw.conf ]; then
    grep -E '^ENABLED=' /etc/ufw/ufw.conf || true
  fi
  review "Live UFW rule list not readable non-interactively (sudo password required)"
fi
review "Tencent Security Group rules cannot be read from the host - verify in console"

section "Existing Docker workloads (do not touch)"
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || review "docker ps unavailable"
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' 2>/dev/null || review "docker stats unavailable"
echo "PoC volumes currently present (expect none before first authorized run):"
docker volume ls --filter 'name=domibox-poc' 2>/dev/null || review "volume check unavailable"
echo "PoC networks currently present (expect none before first authorized run):"
docker network ls --filter 'name=domibox-poc' 2>/dev/null || review "network check unavailable"

section "Summary"
echo "This script performs no changes. A 'REVIEW' line is an environment limitation,"
echo "not a claim that the VPS is down or unprovisioned."
