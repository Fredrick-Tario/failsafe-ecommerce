#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs"
STATUS_RE = re.compile(r"status=(\d{3})")


def analyze(path: Path) -> dict:
    counts = Counter()
    for line in path.read_text(errors="replace").splitlines():
        for level in ("INFO", "WARNING", "ERROR", "CRITICAL"):
            if f"level={level}" in line or f" {level}:" in line:
                counts[level] += 1
        match = STATUS_RE.search(line)
        if match and int(match.group(1)) >= 500:
            counts["HTTP_5XX"] += 1
    return counts


def main() -> None:
    files = sorted(LOG_DIR.glob("*.log"))
    if not files:
        raise SystemExit(f"No log files found in {LOG_DIR}")

    for path in files:
        counts = analyze(path)
        print(
            f"{path.name:20} "
            f"INFO={counts['INFO']:4} WARNING={counts['WARNING']:4} "
            f"ERROR={counts['ERROR']:4} CRITICAL={counts['CRITICAL']:4} "
            f"HTTP_5XX={counts['HTTP_5XX']:4}"
        )


if __name__ == "__main__":
    main()