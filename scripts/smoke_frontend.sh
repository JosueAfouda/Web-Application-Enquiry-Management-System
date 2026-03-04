#!/usr/bin/env bash
set -euo pipefail

WEB_URL="${1:-http://localhost:3000}"

check_route() {
  local route="$1"
  local code
  code="$(curl -s -o /tmp/ems_web_smoke.out -w "%{http_code}" "${WEB_URL}${route}")"
  if [[ "$code" != "200" ]]; then
    echo "[smoke:web] FAIL ${route} expected 200 got ${code}"
    cat /tmp/ems_web_smoke.out || true
    exit 1
  fi
  echo "[smoke:web] PASS ${route}"
}

check_route "/"
check_route "/login"
check_route "/enquiries"

echo "[smoke:web] Frontend container is reachable and SPA routing is active"
