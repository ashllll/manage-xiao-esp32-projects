# Cross-Agent Espressif MCP

Use the same two official remote servers wherever the installed AI client supports Streamable HTTP MCP:

| Name | URL | Purpose |
| --- | --- | --- |
| `espressif-documentation` | `https://mcp.espressif.com/docs` | Official documentation search; OAuth required |
| `esp-component-registry` | `https://components.espressif.com/mcp` | ESP-IDF components, versions, dependencies, and examples |

## Synchronize clients

Preview detected changes:

```bash
python3 scripts/configure_mcp_clients.py
```

Apply user/global configuration:

```bash
python3 scripts/configure_mcp_clients.py --apply
```

The script supports Codex, Claude Code, OpenCode, VS Code, LM Studio, and Reasonix. It only targets clients whose CLI, application support directory, application, or existing configuration directory is detected. Configuration files are merged and backed up before changes; unrelated servers and settings are preserved.

## Client behavior

- Codex: stored in `~/.codex/config.toml`; restart Codex after changes. Authenticate with `codex mcp login espressif-documentation` if needed.
- Claude Code: stored at user scope through `claude mcp add --scope user`; open `/mcp` and authenticate in the browser.
- OpenCode: stored in `~/.config/opencode/opencode.json`; run `opencode mcp auth espressif-documentation`.
- VS Code: stored in the user profile `mcp.json`; start the server from the MCP panel and complete OAuth when prompted.
- LM Studio: stored in `~/.lmstudio/mcp.json`; enable MCP use and connect from the Integrations UI.
- Reasonix: stored in `~/.reasonix/config.toml`. The component registry uses native HTTP. Because Reasonix does not currently implement MCP OAuth, the documentation server runs through `npx -y mcp-remote`. The same configuration adds this skill's exact directory to `[skills].paths`; use `/mcp` and `/skills` to inspect it.

OAuth tokens are client-specific and should not be copied between applications. Configuration can be synchronized, but each client may require its own first-use authorization.

## Scope boundary

This setup covers remote research services. The local `idf.py mcp-server` can build, clean, and flash hardware and requires a valid native ESP-IDF project working directory. Configure it per project through EIM; do not install it globally into every agent or silently mix it with PlatformIO-managed ESP-IDF.

Do not claim support for a client merely because it has an AI settings file. If the client has no documented Streamable HTTP MCP support, leave it unchanged and report it as unsupported or unverified.
