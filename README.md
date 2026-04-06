# Agent Evidence MCP

[![Release](https://img.shields.io/github/v/release/xiexie-qiuligao/agent-evidence-mcp?include_prereleases&label=release)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/releases)
[![CI](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/xiexie-qiuligao/agent-evidence-mcp)](./LICENSE)

中文在前，English below.

## 中文

Agent Evidence MCP 是一个面向 agent 的轻量 MCP server。  
它让大模型在执行长期桌面任务、浏览器任务、QA 流程、后台操作时，不只是“完成任务”，还会留下**可复盘、可审查、可分享**的证据链。

你可以把它理解成：

- `MCP`：把本机截图、录屏、归档能力接给 agent
- `Evidence`：把一次执行过程整理成 session、artifacts、timeline、summary
- `Agent-first`：优先服务“长期任务中的关键节点留痕”，而不是做一个普通截图工具

### 它能解决什么问题

- agent 做长任务时，用户看不到过程，也很难知道它做到哪一步
- 只会“截图一下”还不够，真正需要的是关键节点证据、归档路径、任务总结
- 有些图能直接分享，有些图含敏感信息，需要先生成一份 redacted copy

### 核心能力

- 会话化任务留痕：`start_session` / `end_session`
- 关键节点截图：`capture_checkpoint`
- 可选短录屏：`start_recording` / `stop_recording`
- 证据增强：`attach_note` / `ocr_artifact`
- 证据复盘：`compare_artifacts` / `compare_latest_artifacts`
- 隐私保护：`redact_artifact`
- 自动总结：`summary.md`、`timeline.jsonl`

### 适合的场景

- 浏览器后台配置
- 桌面应用操作
- QA 回归验证
- 数据录入或运营流程
- 需要 agent 留下“过程证据”的长期任务

### 一次理想流程

1. 用户让 agent 执行一个长期任务。
2. agent 先创建一个 session。
3. 每到关键节点截图，必要时短录屏。
4. 如果出现错误、确认页、最终结果页，就额外留证据。
5. 结束时返回 session 目录、summary、关键 artifact 路径。

### 当前支持情况

| 能力 | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Session / MCP / CLI | 已实现并本地验证 | 已实现 | 已实现 |
| 截图 | 已实现并本地验证 | 已实现，未实机验证 | 已实现，未实机验证 |
| 录屏 | 已实现并本地验证 | 已实现，未实机验证 | 已实现，未实机验证 |
| Redaction | 已实现并本地验证 | 未实现 | 未实现 |

更详细的支持矩阵见：[support-matrix.md](docs/support-matrix.md)

### 快速开始

安装：

```bash
pip install -e .
```

生成默认配置：

```bash
agent-evidence-mcp init
```

查看默认配置：

```bash
agent-evidence-mcp show-defaults
```

启动一个 session：

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

截一个关键节点：

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully."
```

结束 session：

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

### 典型 Artifact 目录

```text
artifacts/
  <session_id>/
    session.json
    timeline.jsonl
    summary.md
    details/
    screenshots/
    recordings/
```

### 你可以这样对 agent 说

```text
使用 agent-evidence MCP 帮我完成这个长期任务。
开始前先创建一个 session。
每到关键节点截图，错误出现时额外截图。
优先截图，只有在动作过程很重要时才短录屏。
结束后给我 session 目录、summary 路径和最关键的 artifact。
```

### Alpha 说明

这个仓库现在适合以 **alpha** 形态公开使用：

- 核心 CLI / MCP / artifact workflow 已完成
- Windows 是当前最稳的平台
- macOS / Linux 已有后端路径，但真实机器验证还不够充分
- 测试、构建、release、support docs 都已经具备

已知限制见：[known-limitations.md](docs/known-limitations.md)

### 文档入口

- 支持矩阵：[support-matrix.md](docs/support-matrix.md)
- 已知限制：[known-limitations.md](docs/known-limitations.md)
- 客户端配置：[client-configs.md](docs/client-configs.md)
- Prompt recipes：[recipes.md](docs/recipes.md)
- macOS 验证指南：[macos-validation.md](docs/macos-validation.md)
- Linux 验证指南：[linux-validation.md](docs/linux-validation.md)
- Alpha 发布说明草稿：[alpha-release-notes.md](docs/alpha-release-notes.md)
- Examples 索引：[examples/README.md](examples/README.md)

## English

Agent Evidence MCP is a lightweight MCP server for agents that need to leave behind a **reviewable evidence trail** while performing long-running desktop or browser tasks.

This project is not just about taking screenshots. It is about turning an execution run into:

- a session
- a set of artifacts
- a timeline
- a summary
- a shareable handoff package

### What It Does

- session-based task tracking
- milestone screenshots
- optional short recordings
- artifact notes and OCR enrichment
- artifact comparison for review workflows
- redacted screenshot copies for safer sharing
- structured summaries and predictable artifact directories

### Good Fit

- browser admin flows
- desktop operations
- QA verification
- troubleshooting runs
- long-running agent tasks where users want visible checkpoints

### Quickstart

Install from the repo root:

```bash
pip install -e .
```

Write a starter config:

```bash
agent-evidence-mcp init
```

Start a local MCP server:

```bash
agent-evidence-mcp serve
```

Start a session:

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

Capture a checkpoint:

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully."
```

End the session:

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

### Main MCP Tools

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

### Platform Snapshot

| Capability | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Session / MCP / CLI | Implemented and locally validated | Implemented | Implemented |
| Screenshots | Implemented and locally validated | Implemented, not yet locally validated in this repo | Implemented, not yet locally validated in this repo |
| Recording | Implemented and locally validated | Implemented, not yet locally validated in this repo | Implemented, not yet locally validated in this repo |
| Redaction | Implemented and locally validated | Not implemented | Not implemented |

### Why The Name

`Agent Evidence MCP` is intentionally explicit:

- `Agent` makes the intended user clear
- `Evidence` reflects the real value: checkpoints, summaries, and review trails
- `MCP` keeps the integration surface obvious for tool users searching GitHub

### Documentation

- Support matrix: [support-matrix.md](docs/support-matrix.md)
- Known limitations: [known-limitations.md](docs/known-limitations.md)
- Client configs: [client-configs.md](docs/client-configs.md)
- Prompt recipes: [recipes.md](docs/recipes.md)
- Architecture: [architecture.md](docs/architecture.md)
- Release checklist: [release-checklist.md](docs/release-checklist.md)
- Examples index: [examples/README.md](examples/README.md)

### Alpha Status

This repository is ready for honest alpha usage:

- package builds pass
- tests pass
- Windows validation has been run locally
- release docs and support docs are included

If you want stronger cross-platform confidence, the next most valuable step is real macOS and Linux validation on real machines.
