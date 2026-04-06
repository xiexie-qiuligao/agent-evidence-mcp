# Agent Evidence MCP v0.1.0a1

## 中文

### 这是什么

这是 Agent Evidence MCP 的第一个 alpha 预发布版本。

它的目标不是做一个普通截图工具，而是让 agent 在执行长期桌面任务、浏览器任务、QA 流程、后台操作时，自动留下可复盘、可审查、可分享的证据链。

### 这次版本的重点

- 支持 session 化任务留痕
- 支持关键节点截图
- 支持可选短录屏
- 支持 OCR / note / compare 这类复盘增强能力
- 支持 redacted screenshot，用于生成可分享的安全副本
- 同时提供 CLI 和 MCP 两种入口

### 当前平台状态

- Windows：当前最稳，截图、录屏、redaction 都已经做过本地实机验证
- macOS：截图和录屏后端已实现，但还没有在本仓库做真实机器验证
- Linux：截图和录屏后端已实现，但环境依赖更强，还没有在本仓库做真实机器验证

### 已知限制

- 录屏默认关闭，需要显式开启并安装 `ffmpeg`
- OCR 依赖可选后端，例如 Tesseract
- Linux 目前更依赖桌面环境和本地工具情况
- redaction 目前只对 Windows 截图链路做了真实本地验证
- 这个版本优先服务“长期任务证据链”，还不是通用媒体处理工具

### 推荐的第一句提示词

```text
使用 agent-evidence MCP 帮我完成这个长期任务。
开始前先创建一个 session。
每到关键节点截图，错误出现时额外截图。
优先截图，只有在动作过程很重要时才短录屏。
结束后给我 session 目录、summary 路径和最关键的 artifact。
```

## English

### What This Is

This is the first alpha prerelease of Agent Evidence MCP.

The goal is not to build a generic screenshot utility. The goal is to help agents leave behind a reviewable, shareable evidence trail while performing long-running desktop workflows, browser tasks, QA runs, and operational flows.

### Highlights

- Session-based task evidence
- Milestone screenshots
- Optional short recordings
- OCR, notes, and artifact comparison for review workflows
- Redacted screenshot copies for safer sharing
- Both CLI and MCP entry points

### Platform Status

- Windows: strongest support today, with local real-machine validation for screenshots, recording, and redaction
- macOS: screenshot and recording backends are implemented, but not yet locally validated in this repository
- Linux: screenshot and recording backends are implemented, but support is still more environment-dependent and not yet locally validated in this repository

### Known Caveats

- Recording is disabled by default and requires `ffmpeg`
- OCR depends on an optional backend such as Tesseract
- Linux support is still environment-sensitive
- Redaction has only been locally validated on the Windows screenshot path so far
- This release is focused on evidence workflows, not general media tooling

### Recommended First Prompt

```text
Use the agent-evidence MCP server for this long-running task.
Start a session before the task, capture checkpoints at major state changes,
prefer screenshots over recording, and end the session with artifact paths and a short review summary.
```
