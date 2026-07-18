#!/usr/bin/env python3
"""Validate the portable skill layout without client-specific dependencies."""

from __future__ import annotations

from pathlib import Path
import py_compile


SKILL_NAME = "manage-xiao-esp32-projects"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    required = (
        "SKILL.md",
        "LICENSE",
        "agents/openai.yaml",
        "references/workflow.md",
        "scripts/bootstrap_project.py",
        "scripts/validate_project.py",
        "assets/project-template/platformio.ini",
        "assets/project-template/scripts/verify_hardware.py",
    )
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit("Missing skill resources: " + ", ".join(missing))

    text = (root / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise SystemExit("SKILL.md frontmatter delimiters are invalid")
    frontmatter = text.split("---\n", 2)[1]
    keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
    if keys != ["name", "description"]:
        raise SystemExit(f"Portable frontmatter keys are invalid: {keys}")
    if f"name: {SKILL_NAME}" not in frontmatter:
        raise SystemExit("Skill name does not match its directory")

    for script in sorted((root / "scripts").glob("*.py")):
        py_compile.compile(str(script), doraise=True)
    print(f"Skill validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
