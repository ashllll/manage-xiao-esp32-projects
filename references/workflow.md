# XIAO ESP32 project workflow

## Baseline

The bundled template is verified with:

- PlatformIO Core 6.1.19
- `platformio/espressif32@7.0.0`
- ESP-IDF 6.0.0
- MkDocs 1.6.x and Material 9.7.x
- Apple Silicon `darwin_arm64`

Verified on 2026-07-18. At that time Espressif had a newer ESP-IDF 6.0.x patch
release, while PlatformIO Espressif32 7.0.0 officially integrated ESP-IDF
6.0.0. This template chooses the newest officially integrated PlatformIO pair
instead of overriding only the framework package. Recheck both official release
pages whenever creating a long-lived project or deliberately updating the
template.

The platform version controls the ESP-IDF/toolchain version. Use the newest stable PlatformIO platform that officially supports all target boards, pin it exactly, and rebuild all environments. Do not point `platform_packages` at an arbitrary newer ESP-IDF tag unless the matching PlatformIO integration and toolchains are verified too.

## Board matrix

| Environment | PlatformIO board | Flash | Additional configuration |
|---|---|---:|---|
| `xiao_esp32c3` | `seeed_xiao_esp32c3` | 4 MB | RISC-V |
| `xiao_esp32s3` | `seeed_xiao_esp32s3` | 8 MB | Xtensa, Octal PSRAM |
| `xiao_esp32c6` | `seeed_xiao_esp32c6` | 4 MB | RISC-V, 802.15.4 capable |

Use layered defaults through `board_build.cmake_extra_args` and place generated configs at `.pio/sdkconfig-<environment>` through `board_build.esp-idf.sdkconfig_path`. Keep the path flat beneath `.pio` so a clean checkout does not require creating an extra parent directory before the first build.

## Project structure

```text
.github/workflows/       Firmware matrix and MkDocs Pages workflows
docs/                    Reviewed project documentation
include/xiao_pins.h      D0-D10 symbolic mappings
src/                     ESP-IDF application component
platformio.ini           Pinned board environments
sdkconfig.defaults       Shared ESP-IDF defaults
sdkconfig.flash-4mb      C3/C6 Flash override
sdkconfig.xiao-esp32s3   S3 Flash and PSRAM override
mkdocs.yml               Documentation navigation and theme
requirements-docs.txt    Documentation dependencies
```

Add reusable drivers under `components/<device>/` with public headers in `components/<device>/include/`.

## Local commands

```bash
pio run -e xiao_esp32c3
pio run -e xiao_esp32s3
pio run -e xiao_esp32c6

pio run -e xiao_esp32c3 -t upload
pio device list
pio device monitor -b 115200
```

Documentation:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs build --strict
.venv/bin/mkdocs serve
```

## Required verification

Inspect generated configuration after a clean build:

```bash
rg 'CONFIG_ESPTOOLPY_FLASHSIZE|CONFIG_SPIRAM' \
  .pio/build/<environment>/config/sdkconfig.h
```

Expected results:

- C3: `CONFIG_ESPTOOLPY_FLASHSIZE_4MB`
- S3: `CONFIG_ESPTOOLPY_FLASHSIZE_8MB`, `CONFIG_SPIRAM`, `CONFIG_SPIRAM_MODE_OCT`
- C6: `CONFIG_ESPTOOLPY_FLASHSIZE_4MB`

On Apple Silicon:

```bash
uname -m
pio system info
file ~/.platformio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-gcc
file ~/.platformio/packages/toolchain-xtensa-esp-elf/bin/xtensa-esp-elf-gcc
```

Require `arm64`, `darwin_arm64`, and Mach-O arm64. Cross-compilers still produce Xtensa/RISC-V firmware; the `file` check describes the host executable.

## Pin cautions

- C3 GPIO2/GPIO8/GPIO9 affect boot strapping; D6 emits startup UART output.
- S3 GPIO19/GPIO20 normally serve native USB.
- S3 Sense microSD commonly occupies GPIO7/GPIO8/GPIO9/GPIO21.
- S3 base, Sense, and Plus do not share every expansion-pin mapping.
- ESP32 GPIO is not 5 V tolerant.

## CI

Firmware CI builds all three environments and uploads `.bin` plus `flash_args`. Documentation CI runs `mkdocs build --strict` for pull requests and deploys GitHub Pages on `main`.

Do not publish releases automatically unless requested. A release should include firmware, bootloader, partitions, flash arguments, checksums, board variant, PlatformIO platform version, and upgrade notes.
