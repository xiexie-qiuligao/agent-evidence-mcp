# Client Configs

This document collects practical MCP client configuration examples for Task Evidence MCP.

## What This Server Exposes

The server runs locally and is intended to be launched over `stdio`:

```bash
task-evidence-mcp serve
```

Available tools:

- `start_session`
- `capture_checkpoint`
- `capture_screenshot`
- `list_artifacts`
- `start_recording`
- `get_recording_status`
- `stop_recording`
- `attach_note`
- `ocr_artifact`
- `redact_artifact`
- `compare_artifacts`
- `compare_latest_artifacts`
- `end_session`

## Claude Desktop

Anthropic's Claude Desktop documentation shows local MCP servers configured with a `command`, `args`, and `env` block inside `claude_desktop_config.json`.

Example:

```json
{
  "mcpServers": {
    "task-evidence": {
      "command": "task-evidence-mcp",
      "args": ["serve"],
      "env": {}
    }
  }
}
```

If you want the server to use a specific project directory:

```json
{
  "mcpServers": {
    "task-evidence": {
      "command": "task-evidence-mcp",
      "args": ["serve", "--cwd", "D:\\\\my-project"],
      "env": {}
    }
  }
}
```

If you use a custom config file:

```json
{
  "mcpServers": {
    "task-evidence": {
      "command": "task-evidence-mcp",
      "args": [
        "serve",
        "--cwd",
        "D:\\\\my-project",
        "--config",
        "D:\\\\my-project\\\\task-evidence-mcp.toml"
      ],
      "env": {}
    }
  }
}
```

Reference:

- Anthropic Claude Code MCP docs: https://docs.anthropic.com/en/docs/claude-code/mcp

## Generic stdio JSON Pattern

Many MCP clients use a closely related JSON structure for local stdio servers. If your client asks for a command-and-args style configuration, this pattern is usually the right starting point:

```json
{
  "mcpServers": {
    "task-evidence": {
      "command": "task-evidence-mcp",
      "args": ["serve"],
      "env": {}
    }
  }
}
```

Treat this as a portable example and adapt the outer JSON wrapper to your specific client.

This generic pattern is an inference from common local stdio MCP client layouts. The exact outer structure may vary by client.

## Recommended Prompting

After connecting the server, give the agent a short operating instruction:

```text
Use the task-evidence MCP server for long-running UI or desktop work.
Start a session before the task, capture checkpoints at major state changes,
prefer screenshots over recording, and end the session with artifact paths.
```

## Notes

- Recording is disabled by default and requires `recording_enabled = true`.
- Recording also requires a working `ffmpeg` binary.
- macOS recording may require overriding `macos_avfoundation_input`.
- Linux screenshot capture currently depends on `gnome-screenshot`, `grim`, or ImageMagick `import`.
- If the server is started without `--cwd`, artifacts are stored relative to the current working directory of the server process.
