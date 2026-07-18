"""Pure helpers shared by firmware packaging and hardware verification."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


MAX_FIRMWARE_BYTES = 768 * 1024


@dataclass(frozen=True)
class BoardProfile:
    environment: str
    target: str
    board_name: str
    flash_mb: int
    psram_mb: int


PROFILES = {
    "xiao_esp32c3": BoardProfile(
        "xiao_esp32c3", "esp32c3", "Seeed Studio XIAO ESP32C3", 4, 0
    ),
    "xiao_esp32s3": BoardProfile(
        "xiao_esp32s3", "esp32s3", "Seeed Studio XIAO ESP32S3", 8, 8
    ),
    "xiao_esp32c6": BoardProfile(
        "xiao_esp32c6", "esp32c6", "Seeed Studio XIAO ESP32C6", 4, 0
    ),
}


class ValidationError(ValueError):
    """Raised when an artifact or runtime observation violates the profile."""


def select_espressif_port(devices: list[dict[str, str]]) -> str:
    """Return the only native Espressif USB serial port; never guess."""
    matches = [
        device["port"]
        for device in devices
        if "VID:PID=303A:" in device.get("hwid", "").upper()
        and device.get("port", "").startswith("/dev/cu.")
    ]
    if len(matches) != 1:
        raise ValidationError(
            f"expected exactly one Espressif USB serial port, found {len(matches)}: {matches}"
        )
    return matches[0]


def validate_runtime_log(
    text: str, profile: BoardProfile, required_heartbeats: int = 10
) -> dict[str, object]:
    """Validate a complete boot log and return machine-readable observations."""
    if required_heartbeats < 1:
        raise ValidationError("required_heartbeats must be at least 1")
    fatal_patterns = (
        r"Guru Meditation Error",
        r"ESP_ERROR_CHECK failed",
        r"abort\(\) was called",
        r"assert failed:",
        r"Core\s+\d+\s+panic'ed",
        r"Stack canary watchpoint triggered",
        r"watchdog (?:got triggered|timeout)",
        r"Interrupt wdt timeout",
        r"Brownout detector was triggered",
    )
    for pattern in fatal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raise ValidationError(f"runtime failure marker found: {match.group(0)}")

    ready = f"XIAO_RUNTIME_READY version=1 board={profile.board_name}"
    if ready not in text:
        raise ValidationError(f"missing READY marker for {profile.board_name}")

    flash_matches = [int(value) for value in re.findall(r"SPI Flash Size\s*:\s*(\d+)MB", text)]
    if profile.flash_mb not in flash_matches:
        raise ValidationError(
            f"Flash mismatch: expected {profile.flash_mb} MB, observed {flash_matches}"
        )

    psram_matches = [int(value) for value in re.findall(r"Found\s+(\d+)MB PSRAM", text)]
    if profile.psram_mb and profile.psram_mb not in psram_matches:
        raise ValidationError(
            f"PSRAM mismatch: expected {profile.psram_mb} MB, observed {psram_matches}"
        )

    # Only accept heartbeats emitted after this boot's READY marker. Serial
    # buffers may contain complete lines from the firmware that ran before reset.
    runtime_text = text.rsplit(ready, 1)[1]
    counts = [int(value) for value in re.findall(r"heartbeat count=(\d+)", runtime_text)]
    if len(counts) < required_heartbeats:
        raise ValidationError(
            f"expected {required_heartbeats} heartbeats, observed {len(counts)}"
        )
    observed = counts[:required_heartbeats]
    if any(current != previous + 1 for previous, current in zip(observed, observed[1:])):
        raise ValidationError(f"heartbeats are not consecutive: {observed}")

    return {
        "environment": profile.environment,
        "target": profile.target,
        "board_name": profile.board_name,
        "flash_mb": profile.flash_mb,
        "psram_mb": profile.psram_mb,
        "heartbeat_count": len(observed),
        "first_heartbeat": observed[0],
        "last_heartbeat": observed[-1],
        "ready_version": 1,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_version(project: Path) -> str:
    match = re.search(
        r'set\(PROJECT_VER\s+"([^"]+)"\)',
        (project / "CMakeLists.txt").read_text(encoding="utf-8"),
    )
    if not match:
        raise ValidationError("PROJECT_VER is missing from CMakeLists.txt")
    return match.group(1)


def _platform_version(project: Path) -> str:
    match = re.search(
        r"(?m)^platform\s*=\s*(espressif32@\d+\.\d+\.\d+)\s*$",
        (project / "platformio.ini").read_text(encoding="utf-8"),
    )
    if not match:
        raise ValidationError("pinned espressif32 platform is missing")
    return match.group(1)


def _pinned_requirement(project: Path, name: str) -> str:
    match = re.search(
        rf"(?m)^{re.escape(name)}==([^\s#]+)\s*$",
        (project / "requirements-dev.txt").read_text(encoding="utf-8"),
    )
    if not match:
        raise ValidationError(f"pinned {name} requirement is missing")
    return match.group(1)


def _source_state(project: Path) -> tuple[str, bool | None]:
    result = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown", None
    status = subprocess.run(
        ["git", "-C", str(project), "status", "--porcelain", "--untracked-files=normal", "--", "."],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip(), bool(status.stdout.strip())


def _compiler_identity(description: dict[str, object]) -> tuple[str, str]:
    compiler = Path(str(description.get("c_compiler", "")))
    if not compiler.is_file():
        return compiler.name or "unknown", "unknown"
    result = subprocess.run(
        [str(compiler), "--version"], capture_output=True, text=True
    )
    first_line = result.stdout.splitlines()[0].strip() if result.returncode == 0 and result.stdout else "unknown"
    return compiler.name, first_line


def _portable_flash_args(text: str, app_bin: str) -> str:
    if not app_bin:
        raise ValidationError("project description does not name the application binary")
    replacements = {
        "bootloader/bootloader.bin": "bootloader.bin",
        "partition_table/partition-table.bin": "partition-table.bin",
        app_bin: "firmware.bin",
    }
    for source, destination in replacements.items():
        text = text.replace(source, destination)
    references = re.findall(r"(?m)^0x[0-9a-fA-F]+\s+(\S+\.bin)\s*$", text)
    expected = {"bootloader.bin", "partition-table.bin", "firmware.bin"}
    if set(references) != expected or len(references) != len(expected):
        raise ValidationError(f"flash_args does not reference the packaged artifacts: {references}")
    return text


def create_firmware_package(
    project: Path,
    environment: str,
    output_root: Path,
    max_firmware_bytes: int = MAX_FIRMWARE_BYTES,
) -> Path:
    """Create a deterministic, checksummed firmware delivery directory."""
    if environment not in PROFILES:
        raise ValidationError(f"unsupported environment: {environment}")
    project = project.resolve()
    build = project / ".pio" / "build" / environment
    sources = {
        "firmware.bin": build / "firmware.bin",
        "bootloader.bin": build / "bootloader.bin",
        "partition-table.bin": build / "partitions.bin",
    }
    flash_args_source = build / "flash_args"
    if not flash_args_source.is_file():
        sources["flash_args"] = flash_args_source
    missing = [name for name, path in sources.items() if not path.is_file()]
    if missing:
        raise ValidationError("missing build artifacts: " + ", ".join(missing))
    firmware_size = sources["firmware.bin"].stat().st_size
    if firmware_size > max_firmware_bytes:
        raise ValidationError(
            f"firmware.bin is {firmware_size} bytes; limit is {max_firmware_bytes} bytes"
        )

    description_path = build / "project_description.json"
    if not description_path.is_file():
        raise ValidationError("project_description.json is missing")
    description = json.loads(description_path.read_text(encoding="utf-8"))
    profile = PROFILES[environment]
    if description.get("target") != profile.target:
        raise ValidationError(
            f"target mismatch: expected {profile.target}, got {description.get('target')}"
        )

    output = output_root.resolve() / environment
    output.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, object]] = []
    for name, source in sources.items():
        destination = output / name
        shutil.copy2(source, destination)
        files.append(
            {"name": name, "size_bytes": destination.stat().st_size, "sha256": sha256_file(destination)}
        )
    flash_args = output / "flash_args"
    flash_args.write_text(
        _portable_flash_args(
            flash_args_source.read_text(encoding="utf-8"),
            str(description.get("app_bin", "")),
        ),
        encoding="utf-8",
    )
    files.append(
        {"name": flash_args.name, "size_bytes": flash_args.stat().st_size, "sha256": sha256_file(flash_args)}
    )

    compiler_name, compiler_version = _compiler_identity(description)
    source_revision, source_dirty = _source_state(project)

    manifest = {
        "schema_version": 1,
        "project_version": _project_version(project),
        "environment": environment,
        "target": profile.target,
        "board_name": profile.board_name,
        "platform": _platform_version(project),
        "platformio_core_version": _pinned_requirement(project, "platformio"),
        "esp_idf_version": description.get("git_revision", "unknown"),
        "compiler": compiler_name,
        "compiler_version": compiler_version,
        "source_revision": source_revision,
        "source_dirty": source_dirty,
        "max_firmware_bytes": max_firmware_bytes,
        "files": files,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checksum_entries = files + [
        {
            "name": manifest_path.name,
            "sha256": sha256_file(manifest_path),
        }
    ]
    (output / "SHA256SUMS").write_text(
        "".join(f"{entry['sha256']}  {entry['name']}\n" for entry in checksum_entries),
        encoding="utf-8",
    )
    return output
