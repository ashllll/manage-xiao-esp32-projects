# Cross-Agent Skill Distribution

Use the Agent Skills open format: one directory named `manage-xiao-esp32-projects` containing `SKILL.md`, `scripts/`, `references/`, `assets/`, and optional client metadata. Keep the canonical editable copy at:

```text
~/.agents/skills/manage-xiao-esp32-projects
```

Client entries must resolve to that directory, normally through symlinks created by the `skills` CLI. Do not copy and edit independent versions.

## Install globally

From any current copy of the skill, run:

```bash
npx --yes skills add /absolute/path/to/manage-xiao-esp32-projects \
  --global --agent '*' --skill manage-xiao-esp32-projects --yes
```

The global manager supports Claude Code, Cline, Codex, GitHub Copilot, Kimi Code CLI, OpenCode, Pi, and Reasonix. Gemini CLI, OpenCode, GitHub Copilot, and compatible Agent Skills clients can also discover the canonical `~/.agents/skills` directory directly.

For Reasonix, also keep `[skills].paths` in `~/.reasonix/config.toml` pointed at the canonical directory. Run `scripts/configure_mcp_clients.py --apply` after relocating the canonical skill so its path and official Espressif MCP services stay synchronized.

## Verify discovery

Run the bundled cross-Agent audit first:

```bash
python3 scripts/validate_cross_agent_skill.py
```

Run the global inventory:

```bash
npx --yes skills list --global --json
```

Require the `manage-xiao-esp32-projects` entry to report every Agent detected by the manager. For installed interactive clients, additionally use:

| Client | Verification or invocation |
| --- | --- |
| Codex | Start a new task and invoke `$manage-xiao-esp32-projects` |
| Claude Code | Run `/manage-xiao-esp32-projects`; user skills live under `~/.claude/skills` |
| GitHub Copilot CLI | Run `/skills reload`, then `/skills info manage-xiao-esp32-projects` |
| OpenCode | Ask the agent to load `manage-xiao-esp32-projects` with its native skill tool |
| Gemini CLI | Run `/skills list`, then ask it to use `manage-xiao-esp32-projects` |
| Reasonix | Open `/skills` and inspect the canonical path |
| Pi, Cline, Kimi Code CLI | Inspect their skill list or explicitly request `manage-xiao-esp32-projects` |

Restart a client only when it does not support live skill reload.

## Improve without version drift

1. Resolve the selected client entry and confirm it points to `~/.agents/skills/manage-xiao-esp32-projects`. On macOS, use `python3 -c "from pathlib import Path; print(Path('/client/skill/path').resolve())"`; do not assume GNU `realpath` is installed.
2. Edit only the canonical directory.
3. Keep frontmatter portable: `name` and `description` only. Put Codex-only UI metadata in `agents/openai.yaml`, not in `SKILL.md`.
4. When capability or trigger wording changes, update `SKILL.md`, the relevant references/scripts/assets, and `agents/openai.yaml` when its UI text becomes stale.
5. Run the canonical skill validator, `scripts/validate_project.py assets/project-template`, and `scripts/validate_cross_agent_skill.py`.
6. Run the global inventory again and reject missing Agents, broken links, duplicate resolved paths, or client-specific forks.
7. Forward-test representative prompts in a fresh Agent session when a workflow changes materially.

Useful trigger prompts include:

- "Create a XIAO ESP32S3 PlatformIO + ESP-IDF project with MkDocs documentation."
- "Research this I2C peripheral for XIAO ESP32C6 and document its wiring and SDK."
- "Audit my local XIAO ESP32 documents and remove unreliable generated material."
- "Update and validate the global XIAO ESP32 skill for every installed AI Agent."
