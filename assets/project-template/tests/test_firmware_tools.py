from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys

from scripts.firmware_tools import (
    PROFILES,
    ValidationError,
    create_firmware_package,
    select_espressif_port,
    sha256_file,
    validate_runtime_log,
)


class RuntimeLogTests(unittest.TestCase):
    def test_valid_s3_log(self) -> None:
        heartbeats = "\n".join(f"heartbeat count={value} uptime_ms={value * 1000}" for value in range(4, 14))
        log = "\n".join(
            [
                "I boot.esp32s3: SPI Flash Size : 8MB",
                "I esp_psram: Found 8MB PSRAM device",
                "I xiao_esp32: XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32S3",
                heartbeats,
            ]
        )
        result = validate_runtime_log(log, PROFILES["xiao_esp32s3"], 10)
        self.assertEqual(result["first_heartbeat"], 4)
        self.assertEqual(result["last_heartbeat"], 13)

    def test_nonconsecutive_heartbeat_fails(self) -> None:
        log = "\n".join(
            [
                "SPI Flash Size : 4MB",
                "XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3",
                "heartbeat count=1",
                "heartbeat count=3",
            ]
        )
        with self.assertRaisesRegex(ValidationError, "not consecutive"):
            validate_runtime_log(log, PROFILES["xiao_esp32c3"], 2)

    def test_wrong_board_marker_fails(self) -> None:
        log = "SPI Flash Size : 8MB\nXIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3"
        with self.assertRaisesRegex(ValidationError, "missing READY"):
            validate_runtime_log(log, PROFILES["xiao_esp32s3"], 1)

    def test_panic_marker_fails(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Guru Meditation"):
            validate_runtime_log("Guru Meditation Error", PROFILES["xiao_esp32s3"], 1)

    def test_common_fatal_markers_fail(self) -> None:
        for marker in (
            "assert failed: queue.c:99",
            "Core  0 panic'ed (LoadProhibited)",
            "Stack canary watchpoint triggered",
            "Task watchdog got triggered",
            "Brownout detector was triggered",
        ):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValidationError, "runtime failure"):
                validate_runtime_log(marker, PROFILES["xiao_esp32s3"], 1)

    def test_heartbeats_before_ready_are_ignored(self) -> None:
        log = "\n".join(
            [
                "heartbeat count=40",
                "SPI Flash Size : 4MB",
                "XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3",
                "heartbeat count=1",
                "heartbeat count=2",
            ]
        )
        result = validate_runtime_log(log, PROFILES["xiao_esp32c3"], 2)
        self.assertEqual((result["first_heartbeat"], result["last_heartbeat"]), (1, 2))

    def test_only_heartbeats_after_latest_ready_are_accepted(self) -> None:
        ready = "XIAO_RUNTIME_READY version=1 board=Seeed Studio XIAO ESP32C3"
        log = "\n".join(
            [
                "SPI Flash Size : 4MB",
                ready,
                "heartbeat count=1",
                "heartbeat count=2",
                ready,
            ]
        )
        with self.assertRaisesRegex(ValidationError, "expected 2 heartbeats"):
            validate_runtime_log(log, PROFILES["xiao_esp32c3"], 2)


class PortSelectionTests(unittest.TestCase):
    def test_selects_only_native_espressif_port(self) -> None:
        devices = [
            {"port": "/dev/cu.other", "hwid": "n/a"},
            {"port": "/dev/cu.usbmodem1", "hwid": "USB VID:PID=303A:1001"},
        ]
        self.assertEqual(select_espressif_port(devices), "/dev/cu.usbmodem1")

    def test_refuses_ambiguous_ports(self) -> None:
        devices = [
            {"port": "/dev/cu.usbmodem1", "hwid": "USB VID:PID=303A:1001"},
            {"port": "/dev/cu.usbmodem2", "hwid": "USB VID:PID=303A:1001"},
        ]
        with self.assertRaisesRegex(ValidationError, "exactly one"):
            select_espressif_port(devices)


class PackageTests(unittest.TestCase):
    def make_project(self, root: Path, firmware_size: int = 128) -> Path:
        root.mkdir(parents=True)
        (root / "CMakeLists.txt").write_text('set(PROJECT_VER "0.3.0")\n', encoding="utf-8")
        (root / "platformio.ini").write_text(
            "[env]\nplatform = espressif32@7.0.1\n", encoding="utf-8"
        )
        (root / "requirements-dev.txt").write_text("platformio==6.1.19\n", encoding="utf-8")
        build = root / ".pio" / "build" / "xiao_esp32s3"
        build.mkdir(parents=True)
        (build / "firmware.bin").write_bytes(b"f" * firmware_size)
        (build / "bootloader.bin").write_bytes(b"b")
        (build / "partitions.bin").write_bytes(b"p")
        (build / "flash_args").write_text(
            "--flash-mode dio\n0x0 bootloader/bootloader.bin\n"
            "0x8000 partition_table/partition-table.bin\n0x10000 test_app.bin\n",
            encoding="utf-8",
        )
        (build / "project_description.json").write_text(
            json.dumps({"target": "esp32s3", "git_revision": "6.0.1", "app_bin": "test_app.bin"}),
            encoding="utf-8",
        )
        return root

    def test_creates_manifest_and_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory) / "project")
            output = create_firmware_package(project, "xiao_esp32s3", Path(directory) / "dist")
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_version"], "0.3.0")
            self.assertEqual(manifest["esp_idf_version"], "6.0.1")
            self.assertEqual(manifest["platformio_core_version"], "6.1.19")
            self.assertIsNone(manifest["source_dirty"])
            self.assertEqual(
                (output / "flash_args").read_text(encoding="utf-8").splitlines()[1:],
                ["0x0 bootloader.bin", "0x8000 partition-table.bin", "0x10000 firmware.bin"],
            )
            self.assertIn(sha256_file(output / "manifest.json"), (output / "SHA256SUMS").read_text())

    def test_size_limit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory) / "project", firmware_size=9)
            with self.assertRaisesRegex(ValidationError, "limit is 8"):
                create_firmware_package(project, "xiao_esp32s3", Path(directory) / "dist", 8)

    def test_missing_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory) / "project")
            (project / ".pio" / "build" / "xiao_esp32s3" / "bootloader.bin").unlink()
            with self.assertRaisesRegex(ValidationError, "bootloader.bin"):
                create_firmware_package(project, "xiao_esp32s3", Path(directory) / "dist")


class HardwareCliTests(unittest.TestCase):
    def test_json_error_when_platformio_is_missing(self) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "verify_hardware.py"
        environment = os.environ.copy()
        environment["PATH"] = ""
        result = subprocess.run(
            [sys.executable, str(script), "--environment", "xiao_esp32s3", "--json-output"],
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["stage"], "environment")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
