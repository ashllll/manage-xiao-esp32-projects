#!/usr/bin/env python3
"""Validate a XIAO ESP32 boot over USB, optionally flashing first."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from firmware_tools import PROFILES, ValidationError, select_espressif_port, validate_runtime_log


def pio_devices(pio: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [pio, "device", "list", "--json-output"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def capture_boot(port: str, timeout: float) -> str:
    import serial

    with serial.Serial(port, 115200, timeout=0.2) as monitor:
        monitor.reset_input_buffer()
        monitor.dtr = False
        monitor.rts = True
        time.sleep(0.15)
        monitor.rts = False
        deadline = time.monotonic() + timeout
        chunks: list[bytes] = []
        while time.monotonic() < deadline:
            data = monitor.read(4096)
            if data:
                chunks.append(data)
    return b"".join(chunks).decode("utf-8", "replace")


def emit(payload: dict[str, object], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, choices=PROFILES)
    parser.add_argument("--port", default="auto")
    parser.add_argument("--heartbeats", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--flash", action="store_true", help="Explicitly authorize a firmware upload")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()
    pio = shutil.which("pio")
    if not pio:
        emit(
            {"status": "failed", "stage": "environment", "error": "PlatformIO Core is not available on PATH"},
            args.json_output,
        )
        return 2

    try:
        port = select_espressif_port(pio_devices(pio)) if args.port == "auto" else args.port
        if args.flash:
            subprocess.run(
                [pio, "run", "-e", args.environment, "-t", "upload", "--upload-port", port],
                cwd=Path(__file__).resolve().parent.parent,
                check=True,
                capture_output=args.json_output,
                text=args.json_output,
            )
        log = capture_boot(port, args.timeout)
        observations = validate_runtime_log(log, PROFILES[args.environment], args.heartbeats)
        observations.update({"port": port, "flashed": args.flash, "status": "passed"})
        emit(observations, args.json_output)
        return 0
    except subprocess.CalledProcessError as error:
        emit({"status": "failed", "stage": "command", "error": str(error)}, args.json_output)
        return 3
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as error:
        emit({"status": "failed", "stage": "runtime", "error": str(error)}, args.json_output)
        return 4


if __name__ == "__main__":
    sys.exit(main())
