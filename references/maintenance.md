# Reference and template maintenance

## Local reference library

Resolve the optional library from `XIAO_ESP32_REFERENCE_ROOT`; when unset, use `~/ESP32_资料整理` if it exists. All paths below are relative to that root:

- `官方文档/Seeed_XIAO_ESP32S3_Getting_Started/`: reviewed S3 official mirror and resources.
- `归档/SeeedStudioXIAOESP32_2026-07-18/`: former XIAO working directory archive.
- `02_PlatformIO项目/`: historical project entry points.
- `03_文档资料/`: trusted-entry instructions only; old generated-note symlinks were removed.
- `04_硬件_数据手册/`: peripheral datasheets and schematics.
- `清理记录_2026-07-18.md`: removed derived documents, reasons, and recovery status.

Do not copy the whole library into a project or skill. Link or index it and keep large assets centralized.
Do not regenerate the removed full-home `manifest.csv`, `_raw_hits/`, or low-trust document symlink farm. Prefer a small curated index. Treat material in quarantine or recovery directories, including `~/.Trash/ESP32资料清理_*`, as recovery-only rather than a research source.

## Quarantined derived material

The earlier Kimi S3 handbook and the Downloads-based C6 skill were quarantined on 2026-07-18 because their generated claims, framework boundaries, and pinned versions were not reliably verified. Do not search for or restore them as implementation sources. Use this skill's template, the curated project documentation, and current official sources instead.

## Official sources

- C3: `https://wiki.seeedstudio.com/cn/XIAO_ESP32C3_Getting_Started/`
- S3: `https://wiki.seeedstudio.com/cn/xiao_esp32s3_getting_started/`
- C6: `https://wiki.seeedstudio.com/cn/xiao_esp32c6_getting_started/`
- Seeed source: `https://github.com/Seeed-Studio/wiki-documents`
- ESP-IDF: `https://docs.espressif.com/projects/esp-idf/en/latest/`
- PlatformIO platform: `https://registry.platformio.org/platforms/platformio/espressif32`

When current facts matter, browse the official source and record the verification date. Do not silently replace local official mirrors; preserve provenance and source URLs.

## Updating the bundled template

Resolve the optional canonical working project from `XIAO_ESP32_PROJECT_ROOT`; when unset, use `~/code/esp/xiao_esp32` if it exists.

To update `assets/project-template/`:

1. Validate the working project fully.
2. Copy only source-controlled project files.
3. Exclude `.git/`, `.pio/`, `.venv/`, `site/`, `.DS_Store`, generated `sdkconfig`, and firmware outputs.
4. Run `scripts/validate_project.py assets/project-template` structurally.
5. Scaffold a temporary directory with `scripts/bootstrap_project.py` and compare its file inventory with the template.
6. Run the skill validator.

Keep local reference-library paths configurable and optional; never require the external library for firmware or MkDocs builds.

## Archival checklist

Before removing a requested source directory, capture:

- source and destination absolute paths;
- total size and regular-file count;
- symlink count and broken-link count;
- exact archive name and date;
- repaired and removed alias counts;
- post-migration source existence and archive existence.

If the destination already exists, stop rather than merge ambiguously. If copying across filesystems, compare file counts and checksums before deleting the source.
