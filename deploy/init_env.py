#!/usr/bin/env python3
"""Create first-run credentials privately; never rotate or overwrite live secrets."""
from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def initialise(path: Path) -> bool:
    # O_EXCL also refuses symlinks, including dangling ones. Mode applies from
    # creation, so credentials are never temporarily world-readable.
    content = (
        "INFLUX_ORG=otlab\nINFLUX_BUCKET=vessel\n"
        f"INFLUX_TOKEN={secrets.token_hex(32)}\n"
        f"INFLUX_PASSWORD={secrets.token_hex(24)}\n"
        f"GRAFANA_ADMIN_PASSWORD={secrets.token_hex(24)}\n"
    )
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "w") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=ROOT / ".env")
    args = parser.parse_args()
    if initialise(args.path):
        print("Created private first-run credentials. Values were not printed.")
    else:
        print("Existing credential file preserved unchanged; no secret rotation attempted.")
    print("Next: ./labctl secrets-check (existing placeholders or permissions may still need attention).")


if __name__ == "__main__":
    main()
