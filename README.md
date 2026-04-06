# Agent Evidence MCP

[![Release](https://img.shields.io/github/v/release/xiexie-qiuligao/agent-evidence-mcp?include_prereleases&label=release)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/releases)
[![CI](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/xiexie-qiuligao/agent-evidence-mcp)](./LICENSE)

![Agent Evidence MCP hero](docs/assets/hero.svg)

中文在前，English below.

## 中文

Agent Evidence MCP 是一个面向 agent 的轻量 MCP server。  
它的重点不是“多一个截图工具”，而是把一次长任务整理成一条可复盘的证据链：

- 一个 `session`
- 一组 `artifacts`
- 一份 `timeline`
- 一份 `summary`
- 一套适合交付和复盘的目录结构

### 它适合谁

- 让 agent 执行浏览器或桌面长流程，但又想看到关键节点的人
- 需要把执行过程交给同事、客户或 QA 复盘的人
- 希望把截图、录屏、备注、OCR 和总结放进同一个 session 目录的人
- 想找一个面向 MCP 的轻量证据链工具，而不是通用媒体处理平台的人

### 它能做什么

- 会话化任务留痕：`start_session` / `end_session`
- 关键节点截图：`capture_checkpoint`
- 可选短录屏：`start_recording` / `stop_recording`
- 证据增强：`attach_note` / `ocr_artifact`
- 证据复盘：`compare_artifacts` / `compare_latest_artifacts`
- 隐私保护：`redact_artifact`
- 自动总结：`summary.md` / `timeline.jsonl`

### 适合的任务

- 浏览器后台配置
- 桌面应用操作
- QA 回归验证
- 数据录入或运营流程
- 需要 agent 留下“过程证据”的长期任务

### 平台事实

- Windows 是当前最稳的平台，截图、录屏和 redaction 都做过本地实机验证
- macOS 和 Linux 已经接入截图/录屏后端，适合 alpha 用户试用，但还需要更多真实机器反馈
- Linux 的可用性更依赖桌面环境与本机工具，比如 `gnome-screenshot`、`grim`、`import`、`ffmpeg`
- 这个项目目前优先保证“长期任务证据链”体验，不承诺通用媒体场景的全面兼容

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

启动 MCP server：

```bash
agent-evidence-mcp serve
```

启动一个 session：

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

截图一个关键节点：

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully."
```

结束 session：

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

### 校验发布产物

```bash
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1-py3-none-any.whl SHA256
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1.tar.gz SHA256
```

下载 release 时，也可以直接对照 `SHA256SUMS.txt`。

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

### Release 资产与校验

- 最新 prerelease 页面会同步提供最短安装片段、适用人群和平台边界
- `SHA256SUMS.txt` 会作为 release 资产上传，方便下载后核验
- 如果你只想快速判断这个项目适不适合你，先看 release 页面和 [support-matrix.md](docs/support-matrix.md)

### 文档入口

- 支持矩阵：[support-matrix.md](docs/support-matrix.md)
- 已知限制：[known-limitations.md](docs/known-limitations.md)
- 客户端配置：[client-configs.md](docs/client-configs.md)
- Prompt recipes：[recipes.md](docs/recipes.md)
- 架构说明：[architecture.md](docs/architecture.md)
- Alpha 发布说明草稿：[alpha-release-notes.md](docs/alpha-release-notes.md)
- Examples 索引：[examples/README.md](examples/README.md)

### Alpha 状态

这个仓库已经适合以 **alpha** 形态公开使用：

- 核心 CLI / MCP / artifact workflow 已完成
- Windows 是当前最稳的平台
- macOS / Linux 已有后端路径，但真实机器验证还不够充分
- 测试、构建、release、support docs 都已经具备

已知限制见：[known-limitations.md](docs/known-limitations.md)

## English

Agent Evidence MCP is a lightweight MCP server for agents that need to leave behind a reviewable evidence trail while performing long-running desktop or browser tasks.

This project is not just about taking screenshots. It turns an execution run into:

- a `session`
- a set of `artifacts`
- a `timeline`
- a `summary`
- a shareable handoff package

### Who It Is For

- people who let an agent drive a desktop or browser workflow and want visible milestone evidence
- teams that need a handoff package with screenshots, notes, OCR hints, and a summary
- users who want one session directory instead of loose screenshots and ad-hoc recordings
- early adopters looking for a focused MCP evidence workflow rather than a general-purpose media toolkit

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

### Platform Truth

- Windows is the honest default today: screenshots, recording, and redaction have all been locally exercised on a real machine in this repository
- macOS and Linux already have code paths for screenshots and recording, but they still need broader real-machine validation
- Linux support is the most environment-sensitive because it depends on the available desktop tooling and display setup
- This alpha is optimized for evidence workflows, not every possible screen-capture or media-processing scenario

More detail is available in [support-matrix.md](docs/support-matrix.md).

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

### Verify Release Artifacts

```bash
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1-py3-none-any.whl SHA256
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1.tar.gz SHA256
```

If you download from GitHub Releases, compare the output with `SHA256SUMS.txt`.

### Example Artifact Layout

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

### Suggested First Prompt

```text
Use the agent-evidence MCP server for this long-running task.
Start a session before the task, capture checkpoints at major state changes,
prefer screenshots over recording, and end the session with artifact paths and a short review summary.
```

### Release Assets And Checksums

- the prerelease page includes the shortest-path install snippet, audience framing, and platform truth for quick evaluation
- `SHA256SUMS.txt` is shipped with the release assets so downloaded wheels and source archives can be verified
- if you are scanning the project quickly, start from the release page and the support matrix

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

### Documentation

- Support matrix: [support-matrix.md](docs/support-matrix.md)
- Known limitations: [known-limitations.md](docs/known-limitations.md)
- Client configs: [client-configs.md](docs/client-configs.md)
- Prompt recipes: [recipes.md](docs/recipes.md)
- Architecture: [architecture.md](docs/architecture.md)
- Release checklist: [release-checklist.md](docs/release-checklist.md)
- Alpha release notes draft: [alpha-release-notes.md](docs/alpha-release-notes.md)
- Examples index: [examples/README.md](examples/README.md)

### Alpha Status

This repository is ready for honest alpha usage:

- package builds pass
- tests pass
- Windows validation has been run locally
- release docs and support docs are included

If you want stronger cross-platform confidence, the next most valuable step is real macOS and Linux validation on real machines.
