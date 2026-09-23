#!/usr/bin/env python3
import argparse
import ipaddress
import time
from urllib.parse import urlparse

import httpx


def require_local(url: str) -> None:
    host = urlparse(url).hostname
    if host not in {"localhost", "127.0.0.1"}:
        try:
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError
        except ValueError as exc:
            raise SystemExit(
                "Refusing non-local target. This learning tool only targets localhost."
            ) from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["bad-request", "payment-decline", "small-burst"])
    args = parser.parse_args()

    if args.mode == "bad-request":
        url = "http://127.0.0.1:8004/orders"
        require_local(url)
        response = httpx.post(url, json={"customer_id": "", "items": []}, timeout=2)
        print(response.status_code, response.text)

    elif args.mode == "payment-decline":
        url = "http://127.0.0.1:8005/payments/authorize"
        require_local(url)
        response = httpx.post(
            url,
            json={
                "order_id": "11111111-1111-1111-1111-111111111111",
                "amount": "60000.00",
                "payment_method": "TEST",
            },
            timeout=2,
        )
        print(response.status_code, response.text)

    else:
        url = "http://127.0.0.1:8004/health"
        require_local(url)
        for i in range(20):
            response = httpx.get(url, timeout=2)
            print(f"request={i + 1} status={response.status_code}")
            time.sleep(0.05)


if __name__ == "__main__":
    main()
