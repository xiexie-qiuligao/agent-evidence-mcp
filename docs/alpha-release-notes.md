# Agent Evidence MCP v0.1.0a1

![Agent Evidence MCP hero](https://raw.githubusercontent.com/xiexie-qiuligao/agent-evidence-mcp/main/docs/assets/hero.svg)

## 中文

### 这是什么

这是 Agent Evidence MCP 的第一个 alpha 预发布版本。

它的重点不是做一个普通截图工具，而是让 agent 在执行长期桌面任务、浏览器任务、QA 流程和后台操作时，自动留下可复盘、可审查、可分享的证据链。

### 这次版本的重点

- 支持 session 化任务留痕
- 支持关键节点截图
- 支持可选短录屏
- 支持 note、OCR、artifact compare 这类复盘增强能力
- 支持 redacted screenshot，用于生成可分享的安全副本
- 同时提供 CLI 和 MCP 两种入口

### 最短安装路径

```bash
pip install -e .
agent-evidence-mcp init
agent-evidence-mcp serve
```

### 适合谁

- 让 agent 执行浏览器或桌面长流程，但又想看到关键节点的人
- 需要把执行过程交给同事、客户或 QA 复盘的人
- 想要一个以 session、timeline、summary 为核心的证据链工具的人
- 想找 MCP 工作流工具，而不是通用截图软件的人

### 平台事实

- Windows：当前最稳，截图、录屏和 redaction 都做过本地实机验证
- macOS：截图和录屏后端已实现，但还没有在本仓库完成真实机器验证
- Linux：截图和录屏后端已实现，但更依赖桌面环境和本机工具，还没有在本仓库完成真实机器验证

### 已知限制

- 录屏默认关闭，需要显式开启并安装 `ffmpeg`
- OCR 依赖可选后端，例如 Tesseract
- Linux 对本机桌面环境和 capture 工具更敏感
- redaction 目前只对 Windows 截图链路做了真实本地验证
- 这个版本优先服务“长期任务证据链”，还不是通用媒体处理工具

### 校验与发布资产

- release 页面会附带 `SHA256SUMS.txt`
- 可用它校验 wheel 和 source archive
- 如果你想先判断项目适不适合自己，先看支持矩阵和已知限制

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

- session-based task evidence
- milestone screenshots
- optional short recordings
- notes, OCR, and artifact comparison for review workflows
- redacted screenshot copies for safer sharing
- both CLI and MCP entry points

### Shortest Install Path

```bash
pip install -e .
agent-evidence-mcp init
agent-evidence-mcp serve
```

### Who It Is For

- people who let an agent drive a desktop or browser workflow and want visible milestone evidence
- teams that need a handoff package with screenshots, notes, OCR hints, and a summary
- users who want a session-oriented evidence workflow rather than loose screenshots
- early adopters looking for a focused MCP tool instead of a general-purpose screen utility

### Platform Truth

- Windows: the strongest platform today, with local real-machine validation for screenshots, recording, and redaction
- macOS: screenshot and recording backends are implemented, but not yet locally validated in this repository
- Linux: screenshot and recording backends are implemented, but support is more environment-dependent and not yet locally validated in this repository

### Known Caveats

- recording is disabled by default and requires `ffmpeg`
- OCR depends on an optional backend such as Tesseract
- Linux support is still environment-sensitive
- redaction has only been locally validated on the Windows screenshot path so far
- this release is focused on evidence workflows, not general media tooling

### Checksums And Release Assets

- the release includes `SHA256SUMS.txt`
- use it to verify the wheel and source archive
- if you are evaluating the project quickly, start from the support matrix and known limitations

### Recommended First Prompt

```text
Use the agent-evidence MCP server for this long-running task.
Start a session before the task, capture checkpoints at major state changes,
prefer screenshots over recording, and end the session with artifact paths and a short review summary.
```
