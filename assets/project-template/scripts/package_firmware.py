#!/usr/bin/env python3
"""Package one built PlatformIO environment for reliable delivery."""

from __future__ import annotations

import argparse
from pathlib import Path

from firmware_tools import MAX_FIRMWARE_BYTES, PROFILES, ValidationError, create_firmware_package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, choices=PROFILES)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--max-firmware-bytes", type=int, default=MAX_FIRMWARE_BYTES)
    args = parser.parse_args()
    try:
        output = create_firmware_package(
            args.project, args.environment, args.output_dir, args.max_firmware_bytes
        )
    except (OSError, ValueError, ValidationError) as error:
        parser.exit(1, f"Packaging failed: {error}\n")
    print(f"Firmware package: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
