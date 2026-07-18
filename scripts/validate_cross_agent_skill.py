#!/usr/bin/env python3
"""Audit the canonical skill and its discovery by installed AI agents."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib


SKILL_NAME = "manage-xiao-esp32-projects"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"FAIL: {message}")


def run_json(command: list[str]) -> object:
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=45,
    )
    return json.loads(result.stdout)


def main() -> int:
    home = Path.home()
    canonical = home / ".agents" / "skills" / SKILL_NAME
    errors: list[str] = []

    if not (canonical / "SKILL.md").is_file():
        fail(f"missing canonical SKILL.md at {canonical}", errors)
        return 1

    print(f"canonical: {canonical}")
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "references/cross-agent-skills.md",
        "scripts/bootstrap_project.py",
        "scripts/configure_mcp_clients.py",
        "scripts/validate_cross_agent_skill.py",
        "scripts/validate_project.py",
        "assets/project-template/platformio.ini",
        "assets/project-template/mkdocs.yml",
    ]
    for relative in required:
        if not (canonical / relative).is_file():
            fail(f"missing required resource: {relative}", errors)

    text = (canonical / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail("SKILL.md has invalid frontmatter delimiters", errors)
    else:
        frontmatter = text.split("---\n", 2)[1]
        keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
        if keys != ["name", "description"]:
            fail(f"portable frontmatter must contain only name and description, got {keys}", errors)
        if f"name: {SKILL_NAME}" not in frontmatter:
            fail("frontmatter name does not match the skill directory", errors)

    aliases = {
        "Codex": home / ".codex" / "skills" / SKILL_NAME,
        "Claude Code": home / ".claude" / "skills" / SKILL_NAME,
        "Pi": home / ".pi" / "agent" / "skills" / SKILL_NAME,
        "Reasonix": home / ".reasonix" / "skills" / SKILL_NAME,
    }
    for client, alias in aliases.items():
        client_root_exists = alias.parent.parent.exists()
        if not client_root_exists:
            continue
        if not alias.exists():
            fail(f"{client} entry is missing: {alias}", errors)
        elif alias.resolve() != canonical:
            fail(f"{client} resolves to a divergent copy: {alias.resolve()}", errors)
        else:
            print(f"alias: {client} -> canonical")

    reasonix_config = home / ".reasonix" / "config.toml"
    if reasonix_config.is_file():
        config = tomllib.loads(reasonix_config.read_text(encoding="utf-8"))
        configured = [Path(value).expanduser().resolve() for value in config.get("skills", {}).get("paths", [])]
        if canonical not in configured:
            fail("Reasonix [skills].paths does not include the canonical skill", errors)
        elif configured.count(canonical) != 1:
            fail("Reasonix contains duplicate paths to the canonical skill", errors)
        else:
            print("reasonix: canonical path configured")

    npx = shutil.which("npx")
    if npx:
        try:
            inventory = run_json([npx, "--yes", "skills", "list", "--global", "--json"])
            matches = [item for item in inventory if item.get("name") == SKILL_NAME]
            if len(matches) != 1:
                fail(f"global skills manager reports {len(matches)} entries", errors)
            else:
                entry = matches[0]
                if Path(entry["path"]).resolve() != canonical:
                    fail(f"global manager points to {entry['path']}", errors)
                manager_agents = set(entry.get("agents", []))
                detected_required = {
                    "Codex": shutil.which("codex") is not None,
                    "Claude Code": shutil.which("claude") is not None,
                    "OpenCode": shutil.which("opencode") is not None,
                    "Pi": (home / ".pi" / "agent").exists(),
                    "Reasonix": (home / ".reasonix").exists(),
                    "GitHub Copilot": (home / ".copilot").exists(),
                }
                for client, detected in detected_required.items():
                    if detected and client not in manager_agents:
                        fail(f"global manager does not report detected client: {client}", errors)
                print(f"manager: {len(manager_agents)} Agent adapters report this skill")
        except (OSError, subprocess.SubprocessError, ValueError, KeyError) as error:
            fail(f"cannot verify global skills manager: {error}", errors)
    else:
        fail("npx is unavailable; global Agent inventory cannot be verified", errors)

    opencode = shutil.which("opencode")
    if opencode:
        try:
            result = subprocess.run(
                [opencode, "debug", "skill", "--print-logs", "--log-level", "DEBUG"],
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )
            name_marker = f'"name": "{SKILL_NAME}"'
            location_marker = f'"location": "{canonical / "SKILL.md"}"'
            combined_output = result.stderr + "\n" + result.stdout
            discovered_paths = re.findall(
                rf"service=skill name={re.escape(SKILL_NAME)} (?:existing|duplicate)=([^\s]+)",
                combined_output,
            )
            resolved_discoveries = {Path(value).resolve() for value in discovered_paths}
            json_discovery = name_marker in result.stdout and location_marker in result.stdout
            if not json_discovery and canonical / "SKILL.md" not in resolved_discoveries:
                fail("OpenCode does not report the canonical skill and location", errors)
            else:
                print("opencode: native discovery passed")
        except (OSError, subprocess.SubprocessError) as error:
            fail(f"cannot verify OpenCode discovery: {error}", errors)

    if errors:
        print(f"Cross-Agent validation failed with {len(errors)} error(s).")
        return 1
    print("Cross-Agent validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
