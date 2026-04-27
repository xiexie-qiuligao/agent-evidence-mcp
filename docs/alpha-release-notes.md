# Agent Evidence MCP v0.1.0a1

![Agent Evidence MCP hero](https://raw.githubusercontent.com/xiexie-qiuligao/agent-evidence-mcp/main/docs/assets/hero.svg)

## 中文

这是 Agent Evidence MCP 的第一个 alpha 预发布版本。它是一个面向 agent 长任务的本地证据记录器，不是普通截图软件，也不是浏览器自动化框架。

### 这个版本能做什么

- 创建任务 session
- 在关键节点保存截图
- 在需要展示动作过程时短录屏
- 给证据添加备注和 OCR 文本
- 生成可分享的打码截图副本
- 在结束时整理出 `summary.md` 和 `timeline.jsonl`

### 怎么开始用

```bash
pip install -e .
agent-evidence-mcp init
agent-evidence-mcp serve
```

接入 agent 后，通常可以直接这样说：

```text
Use agent-evidence MCP for this task.
Start a session first.
Capture a screenshot at each major milestone and an extra one on errors.
Prefer screenshots over recording unless motion matters.
When the task is done, give me the summary and the key artifact paths.
```

### 适合谁

- 使用 agent 执行后台流程、桌面操作、QA 或排障任务的人
- 想看见任务过程，而不是只看最终结果的人
- 需要把执行过程交给同事、客户或 QA 复盘的团队

### 平台支持

- Windows: 截图、录屏和 redaction 已完成本地验证
- macOS: 截图和录屏已实现，但尚未在本仓库完成实机验证
- Linux: 截图和录屏已实现，但依赖本地截图工具、X11 和 ffmpeg 环境

详细情况见：

- [support-matrix.md](support-matrix.md)
- [known-limitations.md](known-limitations.md)

### 校验下载文件

release 会附带 `SHA256SUMS.txt`，可用于校验 wheel 和源码包。

## English

This is the first alpha prerelease of Agent Evidence MCP. It is a local evidence recorder for long-running agent work, not a generic screenshot utility or browser automation framework.

### What This Release Can Do

- create task sessions
- capture milestone screenshots
- record short screen segments when motion matters
- attach notes and OCR text
- generate redacted screenshot copies for sharing
- finish with `summary.md` and `timeline.jsonl`

### How To Start

```bash
pip install -e .
agent-evidence-mcp init
agent-evidence-mcp serve
```

Once it is connected to your agent, a prompt like this is usually enough:

```text
Use agent-evidence MCP for this task.
Start a session first.
Capture a screenshot at each major milestone and an extra one on errors.
Prefer screenshots over recording unless motion matters.
When the task is done, give me the summary and the key artifact paths.
```

### Who It Is For

- people using agents for admin flows, desktop tasks, QA, or troubleshooting
- users who want visibility into the process, not just the final answer
- teams that need a reviewable handoff package

### Platform Support

- Windows: screenshots, recording, and redaction have been locally validated
- macOS: screenshots and recording are implemented, but not locally validated in this repo
- Linux: screenshots and recording are implemented, with environment-dependent setup

See also:

- [support-matrix.md](support-matrix.md)
- [known-limitations.md](known-limitations.md)

### Verify Downloads

The release includes `SHA256SUMS.txt` for verifying the wheel and source archive.
