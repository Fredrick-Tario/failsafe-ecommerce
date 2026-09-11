#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess

import httpx

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports"
SERVICES = {
    "auth": "http://127.0.0.1:8001/health",
    "product": "http://127.0.0.1:8002/health",
    "inventory": "http://127.0.0.1:8003/health",
    "order": "http://127.0.0.1:8004/health",
    "payment": "http://127.0.1:8006/health",
}

def service_status(url: str) -> str:
    try:
        response = httpx.get(url, timeout=2)
        return "UP" if response.is_success else f"HTTP {response.status_code}"
    except httpx.RequestError:
        return "DOWN"
    
def postgres_status() -> str:
    result = subprocess.run(["pg_isready", "-q"], check=False)
    return "READY" if result.returncode == 0 else "NOT READY"

def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    disk = shutil.disk_usage("/")
    disk_pct = (disk.used / disk.total) * 100

    lines = [
        f"# FailSafe Operational Report - {now.isoformat()}",
        "",
        "## Service Health",
        "",
        "| Service | Status |",
        "|---|---|",
    ]

    for name, url in SERVICES.items():
        lines.append(f"| {name} | {service_status(url)} |")

    lines.extend([
        "",
        "## Infrastructure",
        "",
        f"- PostgreSQL: **{postgres_status()}**",
        f"- Root filesystem used: **{disk_pct:.1f}%**",
        "",
    ])

    filename = REPORT_DIR / f"ops-report-{now.strftime('%Y%m%dT%H%M%SZ')}.md"
    filename.write_text("\n".join(lines) + "\n")
    print(filename)


if __name__ == "__main__":
    main()