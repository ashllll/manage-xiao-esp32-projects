---
name: manage-xiao-esp32-projects
description: Create, migrate, document, archive, automate, and validate Seeed Studio XIAO ESP32C3/ESP32S3/ESP32C6 projects using PlatformIO, ESP-IDF, MkDocs Material, official Espressif MCP services, and GitHub Actions. Use for scaffolding or maintaining a XIAO ESP32 project, selecting boards, researching peripherals, documenting pins and APIs, configuring Flash/PSRAM, auditing local ESP32 references, removing unreliable derived documentation, generating code from a specification, building firmware, preparing CI/docs, or installing and improving this skill across Codex, Claude Code, Cline, GitHub Copilot, Gemini CLI, Kimi Code CLI, OpenCode, Pi, and Reasonix—especially on Apple Silicon Macs.
---

# Manage XIAO ESP32 Projects

Build from the bundled, verified PlatformIO + ESP-IDF + MkDocs template. Preserve user code and documentation when applying it to an existing project.

## Route the task

- For a new project, run `scripts/bootstrap_project.py` against the requested directory.
- For an existing project, inspect its files first, then copy or adapt only missing template pieces. Never replace user files wholesale.
- For build, board, Flash, PSRAM, documentation, or CI work, read `references/workflow.md`.
- For GPIO buses, Wi-Fi, BLE, Zigbee, Thread, Matter, or framework-specific API work, read `references/board-capabilities.md`.
- For official-source synchronization, local reference consolidation, or deletion after archival, read `references/maintenance.md`.
- For specification-driven project automation, official Espressif MCP integration, or the capability roadmap, read `references/automation-roadmap.md`.
- For installing or synchronizing official MCP servers across AI agents, read `references/cross-agent-mcp.md` and run `scripts/configure_mcp_clients.py`.
- For installing, discovering, invoking, validating, or improving this skill across AI agents, read `references/cross-agent-skills.md`. Keep one canonical copy under `~/.agents/skills/`; do not maintain divergent client-specific copies.
- Treat `assets/project-template/` as the canonical reusable artifact. Do not copy `.git`, `.pio`, `.venv`, `site`, generated `sdkconfig`, or firmware outputs into a new source repository.

## Scaffold a project

Before scaffolding, check the current stable releases from the official ESP-IDF
and PlatformIO Espressif32 release pages. Prefer the newest stable PlatformIO
platform that officially integrates ESP-IDF and supports C3, S3, and C6. Pin
that platform exactly; do not use a beta, release candidate, `latest`, or an
unverified framework override merely to obtain a higher version number.

Run:

```bash
python3 scripts/bootstrap_project.py /absolute/target/path \
  --name project_name \
  --board c3 \
  --init-git
```

Accepted boards are `c3`, `s3`, and `c6`. The template always retains all three PlatformIO environments; `--board` only selects `default_envs`.

After scaffolding:

1. Inspect `platformio.ini`, `include/xiao_pins.h`, and the board-specific `sdkconfig` layers.
2. Update project-specific pin assignments and peripheral pages.
3. Identify the framework before adapting examples. The bundled project uses ESP-IDF; do not paste Arduino APIs into it without an explicit Arduino component or framework change.
4. Keep secrets, Wi-Fi credentials, serial ports, and machine-specific settings out of committed files.
5. Run structural validation before installing or building dependencies.
6. Run full firmware and documentation validation when the environment is available.

## Validate

Structural validation:

```bash
python3 scripts/validate_project.py /absolute/project/path
```

Full validation:

```bash
python3 scripts/validate_project.py /absolute/project/path --build --docs
```

Require these outcomes:

- C3 and C6 use 4 MB Flash.
- S3 uses 8 MB Flash and Octal PSRAM.
- C3, S3, and C6 firmware builds succeed.
- `mkdocs build --strict` succeeds.
- On Apple Silicon, PlatformIO reports `darwin_arm64` and both cross-compilers are Mach-O arm64 executables.

## Maintain documentation

- Keep concise, reviewed project guidance in `docs/`.
- Keep large PDFs, archives, CAD files, and complete vendor mirrors in the external reference library.
- Resolve the optional local reference library from `XIAO_ESP32_REFERENCE_ROOT`, defaulting to `~/ESP32_资料整理`; treat its `README.md` as the curated entry point and do not infer trust merely because a file exists locally.
- Never use material from a quarantine or recovery directory, including paths matching `~/.Trash/ESP32资料清理_*`, as an implementation or documentation source.
- Do not recreate full-home manifests, raw scan dumps, or low-trust document symlink farms. Maintain small, reviewed indexes instead.
- Record every peripheral's power requirements, logic level, wiring, bus settings, SDK source/version, examples, and known conflicts.
- Prefer Seeed Wiki/GitHub and Espressif documentation over derived notes when facts conflict.
- Keep XIAO D0–D10 symbolic mappings in `include/xiao_pins.h`; avoid raw GPIO numbers in application code.
- When local reference documents are corrected, replaced, or removed, update `references/maintenance.md` and any affected files under `assets/project-template/` in the same task. Then validate the skill, validate the template structurally, and scaffold a temporary project to compare its file inventory with the template.

## Use official Espressif MCP services

- Use `espressif-documentation` for current ESP-IDF API, programming guide, and chip-specific documentation queries.
- Use `esp-component-registry` before writing a peripheral driver from scratch. Prefer a compatible, maintained component with examples and a clear license.
- Record the source URL, component or documentation version, target chip, retrieval date, and important constraints in project documentation.
- Treat MCP results as research inputs: verify board-specific electrical and pin facts against the official Seeed XIAO documentation.
- Keep remote documentation MCP calls interactive. Do not build rate-limited remote searches into CI or bulk mirroring jobs.
- Configure supported AI clients at user/global scope rather than treating Codex configuration as the source of truth. Keep authentication tokens in each client's secure store, never in the skill.

## Handle destructive archival safely

Only remove an original directory when the user explicitly requests it. Before doing so:

1. Resolve and print the exact source and archive paths.
2. Inventory size, regular files, and symlinks.
3. Move or copy into a uniquely named archive directory.
4. Verify the archive exists and contains the expected files.
5. Repair aliases pointing to the old root.
6. Remove only stale aliases whose target entities were already absent.
7. Confirm the old path is gone and the reference library has no broken links.
8. Write a migration record beside the archive.

Prefer an atomic move on the same filesystem so recovery remains possible from the archive.

## Guardrails

- Pin `platformio/espressif32`; do not use an unversioned platform in reproducible projects.
- Treat "latest" as the newest stable, officially integrated, three-board-tested PlatformIO/ESP-IDF pair. Record both versions and the verification date.
- Do not assume PlatformIO's default generated `sdkconfig` has the correct Flash size.
- Store generated per-environment `sdkconfig` files inside `.pio/`, never at the repository root.
- Set `PROJECT_VER` explicitly so an empty Git repository can build.
- Do not flash, erase, publish, commit, push, or create a release unless the user requests it.
- Verify actual board variants before applying S3 Sense or Plus camera, microSD, LED, or extra-pin mappings.
- Keep build and documentation generation non-destructive by default. Require an explicit user request before any hardware-writing MCP or command performs flash or erase operations.
- Do not mix PlatformIO-managed ESP-IDF with an independently installed native ESP-IDF toolchain silently. Use the project's PlatformIO environment unless the user explicitly selects a native EIM/ESP-IDF workflow.
- Resolve the real skill path before editing it. After changing the skill, validate the canonical copy and confirm every detected Agent still resolves to that same copy; never optimize one client's stale fork.
