#!/usr/bin/env bash
set -euo pipefail

echo "== DNS =="
getent hosts management.azure.com || true

echo " == HTTPS outbound =="
curl -I --max-time 5 https://management.azure.com/ || true

echo "== Routes =="
ip route

echo "== Listening ports =="
ss -lntup

echo "== Resolver =="
cat /etc/resolv.conf