#!/usr/bin/env python3
"""Synchronize official Espressif remote MCP servers across detected AI clients."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import tomllib


SERVERS = {
    "espressif-documentation": "https://mcp.espressif.com/docs",
    "esp-component-registry": "https://components.espressif.com/mcp",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write configuration; without this flag only show the plan",
    )
    return parser.parse_args()


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default.copy()
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(f"{path.name}.bak.{int(time.time())}")
        shutil.copy2(path, backup)
        print(f"  backup: {backup}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(f"{path.name}.bak.{int(time.time())}")
        shutil.copy2(path, backup)
        print(f"  backup: {backup}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def merge_json_client(path: Path, section: str, style: str, apply: bool) -> None:
    data = load_json(path, {section: {}})
    entries = data.setdefault(section, {})
    if not isinstance(entries, dict):
        raise ValueError(f"expected {section} to be an object in {path}")

    changed = False
    for name, url in SERVERS.items():
        if style == "opencode":
            desired = {"enabled": True, "type": "remote", "url": url}
        elif style == "vscode":
            desired = {"type": "http", "url": url}
        else:
            desired = {"url": url}
        if entries.get(name) != desired:
            entries[name] = desired
            changed = True

    state = "update" if changed else "already configured"
    print(f"{style}: {state} ({path})")
    if changed and apply:
        write_json(path, data)


def cli_has_server(command: str, name: str) -> bool:
    result = subprocess.run(
        [command, "mcp", "get", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
        check=False,
    )
    return result.returncode == 0


def configure_cli(command: str, style: str, apply: bool) -> None:
    executable = shutil.which(command)
    if not executable:
        return
    for name, url in SERVERS.items():
        if cli_has_server(executable, name):
            print(f"{style}: already configured ({name})")
            continue
        print(f"{style}: add {name}")
        if not apply:
            continue
        if style == "codex":
            args = [executable, "mcp", "add", name, "--url", url]
        else:
            args = [
                executable,
                "mcp",
                "add",
                "--transport",
                "http",
                "--scope",
                "user",
                name,
                url,
            ]
        subprocess.run(args, check=True)


def configure_reasonix(home: Path, skill_root: Path, apply: bool) -> None:
    config_path = home / ".reasonix" / "config.toml"
    app_path = Path("/Applications/Reasonix.app")
    if not config_path.exists() and not app_path.exists():
        return

    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    parsed = tomllib.loads(text) if text.strip() else {}
    plugin_names = {item.get("name") for item in parsed.get("plugins", [])}
    paths = list(parsed.get("skills", {}).get("paths", []))
    canonical_root = skill_root.resolve()
    skill_path = str(canonical_root)
    changes: list[str] = []

    normalized_paths: list[str] = []
    canonical_added = False
    for configured_path in paths:
        resolved_path = Path(configured_path).expanduser().resolve()
        if resolved_path == canonical_root:
            if not canonical_added:
                normalized_paths.append(skill_path)
                canonical_added = True
            continue
        normalized_paths.append(configured_path)
    if not canonical_added:
        normalized_paths.append(skill_path)

    if normalized_paths != paths:
        skill_line = "paths = " + json.dumps(normalized_paths, ensure_ascii=False)
        marker = "[skills]"
        if marker in text:
            start = text.index(marker) + len(marker)
            end = text.find("\n[", start)
            if end < 0:
                end = len(text)
            section = text[start:end]
            active_paths = next(
                (line for line in section.splitlines() if line.strip().startswith("paths =")),
                None,
            )
            if active_paths:
                section = section.replace(active_paths, skill_line, 1)
                text = text[:start] + section + text[end:]
            else:
                text = text[:start] + "\n" + skill_line + text[start:]
        else:
            text = text.rstrip() + f"\n\n[skills]\n{skill_line}\n"
        changes.append("skill path")

    if "espressif-documentation" not in plugin_names:
        text = text.rstrip() + (
            "\n\n[[plugins]]\n"
            'name = "espressif-documentation"\n'
            'command = "npx"\n'
            'args = ["-y", "mcp-remote", "https://mcp.espressif.com/docs"]\n'
        )
        changes.append("espressif-documentation")
    if "esp-component-registry" not in plugin_names:
        text = text.rstrip() + (
            "\n\n[[plugins]]\n"
            'name = "esp-component-registry"\n'
            'type = "http"\n'
            'url = "https://components.espressif.com/mcp"\n'
        )
        changes.append("esp-component-registry")

    state = "update " + ", ".join(changes) if changes else "already configured"
    print(f"reasonix: {state} ({config_path})")
    if changes and apply:
        if not text.endswith("\n"):
            text += "\n"
        tomllib.loads(text)
        write_text(config_path, text)


def main() -> int:
    args = parse_args()
    home = Path.home()
    print("mode:", "apply" if args.apply else "dry-run")

    configure_cli("codex", "codex", args.apply)
    configure_cli("claude", "claude", args.apply)

    opencode_dir = home / ".config" / "opencode"
    if shutil.which("opencode") or opencode_dir.exists():
        merge_json_client(opencode_dir / "opencode.json", "mcp", "opencode", args.apply)

    vscode_dir = home / "Library" / "Application Support" / "Code" / "User"
    if vscode_dir.exists():
        merge_json_client(vscode_dir / "mcp.json", "servers", "vscode", args.apply)

    lmstudio_dir = home / ".lmstudio"
    if lmstudio_dir.exists():
        merge_json_client(lmstudio_dir / "mcp.json", "mcpServers", "lmstudio", args.apply)

    configure_reasonix(home, Path(__file__).resolve().parent.parent, args.apply)

    print("OAuth remains client-specific; authenticate espressif-documentation in each client.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
