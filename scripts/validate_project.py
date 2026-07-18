#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED = (
    "platformio.ini",
    "CMakeLists.txt",
    "src/CMakeLists.txt",
    "src/main.c",
    "include/xiao_pins.h",
    "sdkconfig.defaults",
    "sdkconfig.flash-4mb",
    "sdkconfig.xiao-esp32s3",
    "mkdocs.yml",
    "requirements-docs.txt",
    "requirements-dev.txt",
    "scripts/package_firmware.py",
    "scripts/verify_hardware.py",
    "tests/test_firmware_tools.py",
)
ENVIRONMENTS = ("xiao_esp32c3", "xiao_esp32s3", "xiao_esp32c6")
GENERATED_CONFIG = {
    "xiao_esp32c3": ("CONFIG_ESPTOOLPY_FLASHSIZE_4MB", "CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG"),
    "xiao_esp32s3": (
        "CONFIG_ESPTOOLPY_FLASHSIZE_8MB",
        "CONFIG_SPIRAM",
        "CONFIG_SPIRAM_MODE_OCT",
        "CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG",
    ),
    "xiao_esp32c6": ("CONFIG_ESPTOOLPY_FLASHSIZE_4MB", "CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG"),
}


def run(command: list[str], cwd: Path) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def verify_generated_configs(project: Path) -> None:
    for environment, settings in GENERATED_CONFIG.items():
        config = project / ".pio" / "build" / environment / "config" / "sdkconfig.h"
        if not config.is_file():
            raise SystemExit(f"Generated config is missing after build: {config}")
        contents = config.read_text(encoding="utf-8")
        for setting in settings:
            if not re.search(rf"(?m)^#define {re.escape(setting)}(?: 1)?$", contents):
                raise SystemExit(f"{environment} generated config is missing: {setting}")
        if re.search(r"(?m)^#define CONFIG_ESP_CONSOLE_UART 1$", contents):
            raise SystemExit(f"{environment} still enables the UART application console")


def verify_apple_silicon_toolchains(project: Path) -> None:
    if sys.platform != "darwin" or platform.machine() != "arm64":
        return

    system_info = subprocess.run(
        ["pio", "system", "info"], cwd=project, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    ).stdout
    if "darwin_arm64" not in system_info:
        raise SystemExit("PlatformIO does not report System Type darwin_arm64")

    match = re.search(r"(?m)^PlatformIO Core Directory\s+(.+)$", system_info)
    if not match:
        raise SystemExit("Cannot locate the PlatformIO Core Directory")
    packages = Path(match.group(1).strip()) / "packages"
    compilers = (
        packages / "toolchain-riscv32-esp" / "bin" / "riscv32-esp-elf-gcc",
        packages / "toolchain-xtensa-esp-elf" / "bin" / "xtensa-esp-elf-gcc",
    )
    for compiler in compilers:
        if not compiler.is_file():
            raise SystemExit(f"Toolchain executable is missing: {compiler}")
        description = subprocess.run(
            ["file", str(compiler)], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        ).stdout
        if "Mach-O 64-bit executable arm64" not in description:
            raise SystemExit(f"Toolchain is not a native Apple Silicon executable: {description.strip()}")
        print(description.strip())


def verify_delivery_packages(project: Path) -> None:
    expected_references = {"bootloader.bin", "partition-table.bin", "firmware.bin"}
    for environment in ENVIRONMENTS:
        package = project / "dist" / environment
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        if not re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("source_revision", ""))):
            raise SystemExit(f"{environment} manifest has no Git source revision")
        if manifest.get("source_dirty") is not False:
            raise SystemExit(f"{environment} manifest was built from a dirty or unknown source tree")
        if manifest.get("platformio_core_version") != "6.1.19":
            raise SystemExit(f"{environment} manifest has the wrong PlatformIO Core version")
        if manifest.get("compiler_version") in (None, "", "unknown"):
            raise SystemExit(f"{environment} manifest has no compiler version")
        flash_args = (package / "flash_args").read_text(encoding="utf-8")
        references = set(re.findall(r"(?m)^0x[0-9a-fA-F]+\s+(\S+\.bin)\s*$", flash_args))
        if references != expected_references:
            raise SystemExit(f"{environment} flash_args is not self-contained: {references}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a XIAO ESP32 project")
    parser.add_argument("project", type=Path)
    parser.add_argument("--build", action="store_true", help="Build all PlatformIO environments")
    parser.add_argument("--docs", action="store_true", help="Build MkDocs in strict mode")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()

    missing = [name for name in REQUIRED if not (project / name).is_file()]
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))

    ini = (project / "platformio.ini").read_text(encoding="utf-8")
    checks = {
        "pinned platform": r"(?m)^platform\s*=\s*espressif32@\d+\.\d+\.\d+\s*$",
        "C3 environment": r"\[env:xiao_esp32c3\]",
        "S3 environment": r"\[env:xiao_esp32s3\]",
        "C6 environment": r"\[env:xiao_esp32c6\]",
        "generated sdkconfig under .pio": r"board_build\.esp-idf\.sdkconfig_path\s*=\s*\.pio/",
    }
    failed = [label for label, pattern in checks.items() if not re.search(pattern, ini)]
    if failed:
        raise SystemExit("Configuration checks failed: " + ", ".join(failed))
    if "platform = espressif32@7.0.1" not in ini:
        raise SystemExit("Expected PlatformIO Espressif32 7.0.1")

    docs_requirements = (project / "requirements-docs.txt").read_text(encoding="utf-8")
    for requirement in ("mkdocs==1.6.1", "mkdocs-material==9.7.7"):
        if requirement not in docs_requirements:
            raise SystemExit(f"Pinned documentation dependency is missing: {requirement}")
    dev_requirements = (project / "requirements-dev.txt").read_text(encoding="utf-8")
    for requirement in ("platformio==6.1.19", "pyserial==3.5"):
        if requirement not in dev_requirements:
            raise SystemExit(f"Pinned development dependency is missing: {requirement}")

    if "CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y" not in (project / "sdkconfig.flash-4mb").read_text():
        raise SystemExit("4 MB Flash default is missing")
    s3 = (project / "sdkconfig.xiao-esp32s3").read_text()
    for setting in ("CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y", "CONFIG_SPIRAM=y", "CONFIG_SPIRAM_MODE_OCT=y"):
        if setting not in s3:
            raise SystemExit(f"S3 default is missing: {setting}")

    if args.build:
        if not shutil.which("pio"):
            raise SystemExit("pio is not installed")
        for environment in ENVIRONMENTS:
            run(["pio", "run", "-e", environment], project)
        verify_generated_configs(project)
        verify_apple_silicon_toolchains(project)
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], project)
        for environment in ENVIRONMENTS:
            run([sys.executable, "scripts/package_firmware.py", "--environment", environment], project)
        verify_delivery_packages(project)

    if args.docs:
        local_mkdocs = project / ".venv" / "bin" / "mkdocs"
        executable = str(local_mkdocs) if local_mkdocs.is_file() else shutil.which("mkdocs")
        if not executable:
            raise SystemExit("mkdocs is not installed; create .venv and install requirements-docs.txt")
        run([executable, "build", "--strict"], project)

    print(f"Validation passed: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
