# Automation and MCP Roadmap

Use this roadmap when the user wants to turn a XIAO ESP32 idea, peripheral list, or wiring plan into a reproducible project with less manual work.

## Target workflow

The long-term entry point is a checked-in `xiao-project.yaml` specification. It declares:

- project name, XIAO board variant, framework, and required ESP-IDF features;
- peripherals, part numbers, buses, addresses, power and logic levels;
- preferred pins or automatic pin allocation constraints;
- required firmware features, documentation pages, tests, and CI targets;
- whether hardware actions such as serial monitoring or flashing are allowed.

The automation should execute this sequence:

1. Validate the specification without changing files.
2. Query official documentation and the ESP Component Registry.
3. Resolve board capability, dependency, electrical, bus, address, and pin conflicts.
4. Produce a reviewable plan with sources and unresolved decisions.
5. Scaffold or update the project idempotently.
6. Generate component integration, configuration, pin aliases, and MkDocs pages.
7. Run structural checks, all requested board builds, tests, and strict documentation builds.
8. Flash or erase only after an explicit user request.

## Planned capability phases

### Phase 1: Reproducible project specification

Add:

- `assets/project-spec.example.yaml` as the canonical example;
- `references/project-schema.md` for field semantics and examples;
- `scripts/validate_spec.py` for schema and cross-field validation;
- `scripts/automate_project.py --dry-run` to emit a deterministic project plan;
- a small, versioned board capability database for C3, S3, and C6.

Acceptance: the same specification produces the same file plan; invalid board, framework, Flash, PSRAM, or feature combinations fail before writes.

### Phase 2: Peripheral research and component selection

Integrate the global MCP services:

- `espressif-documentation` at `https://mcp.espressif.com/docs` for ESP-IDF documentation;
- `esp-component-registry` at `https://components.espressif.com/mcp` for reusable components and examples.

Normalize each peripheral into a manifest containing source URL, version, license, supported targets, bus, address, power, logic level, example path, and retrieval date. Prefer, in order: an official Espressif component, a vendor-maintained ESP-IDF component, a well-maintained compatible component, then a generated local driver.

Acceptance: every generated integration has traceable sources; uncertain or conflicting facts are surfaced rather than guessed.

### Phase 3: Resource and pin conflict engine

Add `scripts/check_resource_conflicts.py` to model:

- reserved, strapping, USB/JTAG, flash, PSRAM, boot, and variant-specific pins;
- input/output/ADC/PWM/interrupt requirements;
- I2C address collisions, SPI chip selects, UART ownership, and shared-bus settings;
- 3.3 V logic, current budget, regulator limits, and level-shifter requirements;
- radio and protocol constraints for Wi-Fi, BLE, Zigbee, Thread, and Matter.

Acceptance: the tool explains each conflict, cites the relevant board/chip constraint, and proposes safe alternatives without silently rewriting user-selected pins.

### Phase 4: Code and documentation generation

Generate or update only owned regions and files:

- ESP-IDF component dependencies and configuration defaults;
- typed peripheral configuration and symbolic XIAO pin mappings;
- component wrappers, initialization skeletons, and host-testable logic;
- wiring, API/SDK, configuration, troubleshooting, and source-manifest pages;
- MkDocs navigation and Mermaid connection diagrams.

Acceptance: repeated runs are idempotent, manual code outside generated regions is preserved, and generated code compiles for the declared board matrix.

### Phase 5: Closed-loop validation and maintenance

Extend validation with component tests, matrix builds, size reports, documentation link checks, dependency freshness reports, and optional hardware smoke-test recipes. Use remote MCP search interactively, not from CI. Cache durable citations and metadata in the repository.

For native ESP-IDF projects installed through EIM, the optional official local server can run as `eim run "idf.py mcp-server"`. Keep it project-scoped because it needs a valid ESP-IDF working directory. The current template is PlatformIO-managed, so continue using PlatformIO scripts for build and environment selection unless the workflow is explicitly migrated.

Acceptance: automation can stop after research, planning, generation, build, or hardware validation; each stage records its inputs, outputs, and validation result.

## Safety and review gates

- Default to dry-run for migrations and specification-driven updates.
- Show sources, resolved versions, planned file changes, and conflicts before generation.
- Never place credentials, Wi-Fi secrets, serial-port paths, or machine-specific settings in generated committed files.
- Require explicit approval for flash, erase, archive deletion, publishing, commits, pushes, or releases.
- Do not allow generated output to overwrite unrecognized user-owned files.

## Recommended next implementation slice

Implement Phase 1 first, plus a read-only MCP research report for one I2C peripheral. This proves the specification, provenance, conflict-reporting, and idempotency model before adding code generation. Use BME280 or SHT4x as the first fixture because it exercises component discovery, I2C addressing, wiring, configuration, and documentation without requiring complex hardware resources.
