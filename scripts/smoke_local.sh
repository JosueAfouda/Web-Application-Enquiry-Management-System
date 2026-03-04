#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "[smoke] Checking health endpoint: ${BASE_URL}/health"
HTTP_CODE="$(curl -s -o /tmp/ems_health.json -w "%{http_code}" "${BASE_URL}/health")"

if [[ "${HTTP_CODE}" != "200" ]]; then
  echo "[smoke] FAIL: expected HTTP 200 but got ${HTTP_CODE}"
  cat /tmp/ems_health.json || true
  exit 1
fi

if ! grep -q '"status":"ok"' /tmp/ems_health.json && ! grep -q '"status": "ok"' /tmp/ems_health.json; then
  echo "[smoke] FAIL: response body is not {'status':'ok'}"
  cat /tmp/ems_health.json
  exit 1
fi

echo "[smoke] PASS: health endpoint is healthy"
