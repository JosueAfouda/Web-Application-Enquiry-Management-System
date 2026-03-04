#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
WEB_URL="${2:-http://localhost:3000}"
DEMO_USER="${EMS_SMOKE_USER:-admin}"
DEMO_PASS="${EMS_SMOKE_PASS:-admin}"

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

echo "[smoke] Checking auth login endpoint"
LOGIN_CODE="$(
  curl -s -o /tmp/ems_login.json -w "%{http_code}" \
    -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${DEMO_USER}\",\"password\":\"${DEMO_PASS}\"}"
)"

if [[ "${LOGIN_CODE}" != "200" ]]; then
  echo "[smoke] FAIL: /auth/login expected 200 but got ${LOGIN_CODE}"
  cat /tmp/ems_login.json || true
  exit 1
fi

ACCESS_TOKEN="$(sed -n 's/.*\"access_token\":\"\\([^\"]*\\)\".*/\\1/p' /tmp/ems_login.json | head -n 1)"
if [[ -z "${ACCESS_TOKEN}" ]]; then
  echo "[smoke] FAIL: login response did not include access_token"
  cat /tmp/ems_login.json || true
  exit 1
fi
echo "[smoke] PASS: login returned access token"

echo "[smoke] Checking authenticated endpoint: ${BASE_URL}/auth/me"
ME_CODE="$(
  curl -s -o /tmp/ems_me.json -w "%{http_code}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    "${BASE_URL}/auth/me"
)"
if [[ "${ME_CODE}" != "200" ]]; then
  echo "[smoke] FAIL: /auth/me expected 200 but got ${ME_CODE}"
  cat /tmp/ems_me.json || true
  exit 1
fi
echo "[smoke] PASS: authenticated endpoint is healthy"

echo "[smoke] Checking frontend endpoint: ${WEB_URL}/"
WEB_CODE="$(curl -s -o /tmp/ems_web.html -w "%{http_code}" "${WEB_URL}/")"
if [[ "${WEB_CODE}" != "200" ]]; then
  echo "[smoke] FAIL: frontend expected HTTP 200 but got ${WEB_CODE}"
  cat /tmp/ems_web.html || true
  exit 1
fi
echo "[smoke] PASS: frontend is reachable"
