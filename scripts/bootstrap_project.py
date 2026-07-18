#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "project-template"
BOARD_ENVS = {
    "c3": "xiao_esp32c3",
    "s3": "xiao_esp32s3",
    "c6": "xiao_esp32c6",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a XIAO ESP32 PlatformIO project")
    parser.add_argument("target", type=Path, help="New or empty target directory")
    parser.add_argument("--name", default="xiao_esp32", help="CMake-safe project name")
    parser.add_argument("--board", choices=BOARD_ENVS, default="c3")
    parser.add_argument("--init-git", action="store_true", help="Initialize a main-branch Git repository")
    return parser.parse_args()


def require_safe_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", name):
        raise SystemExit("--name must start with a letter/underscore and contain letters, digits, _ or -")


def main() -> int:
    args = parse_args()
    require_safe_name(args.name)
    target = args.target.expanduser().resolve()

    if not TEMPLATE.is_dir():
        raise SystemExit(f"Missing template: {TEMPLATE}")
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, target, dirs_exist_ok=True)

    platformio = target / "platformio.ini"
    text = platformio.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^default_envs\s*=.*$", f"default_envs = {BOARD_ENVS[args.board]}", text, count=1)
    platformio.write_text(text, encoding="utf-8")

    cmake = target / "CMakeLists.txt"
    text = cmake.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^project\([^)]*\)$", f"project({args.name})", text, count=1)
    cmake.write_text(text, encoding="utf-8")

    if args.init_git:
        subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True)

    print(f"Created {args.name} at {target}")
    print(f"Default environment: {BOARD_ENVS[args.board]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

