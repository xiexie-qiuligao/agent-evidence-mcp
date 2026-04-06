# Agent Evidence MCP v0.1.0a1

![Agent Evidence MCP hero](https://raw.githubusercontent.com/xiexie-qiuligao/agent-evidence-mcp/main/docs/assets/hero.svg)

## 中文

让 agent 在执行任务时，自动留下关键截图、短录屏、备注和总结。

这是 Agent Evidence MCP 的第一个 alpha 预发布版本。它更像一个“任务证据工具”，而不是普通截图软件。

### 这个版本能做什么

- 创建任务 session
- 在关键节点截图
- 在需要时短录屏
- 给证据加备注和 OCR 文本
- 对截图进行打码，生成可分享版本
- 在结束时整理出 summary 和 timeline

### 怎么开始用

```bash
pip install -e .
agent-evidence-mcp init
agent-evidence-mcp serve
```

接入 agent 后，你可以直接这样说：

```text
用 agent-evidence MCP 帮我完成这个任务。
开始前先创建一个 session。
每到关键节点截一张图，出错时额外截图。
结束后把 summary 和所有关键产物路径告诉我。
```

### 适合谁

- 让 agent 执行后台流程或桌面任务的人
- 想看到任务中间过程，而不是只看最后结果的人
- 需要把执行过程交给同事、客户或 QA 复盘的人

### 平台支持

- Windows：截图、录屏和 redaction 已完成本地验证
- macOS：截图和录屏已实现
- Linux：截图和录屏已实现

详细情况见：
- [support-matrix.md](support-matrix.md)
- [known-limitations.md](known-limitations.md)

### 校验下载文件

release 会附带 `SHA256SUMS.txt`，可用于校验 wheel 和源码包。

## English

Let your agent leave behind milestone screenshots, short recordings, notes, and a final summary while it works.

This is the first alpha prerelease of Agent Evidence MCP. It is built as a task-evidence tool, not a generic screenshot utility.

### What This Release Can Do

- create task sessions
- capture milestone screenshots
- record short screen segments
- attach notes and OCR text
- generate redacted copies for sharing
- finish with a summary and timeline

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
When the task is done, give me the summary and the key artifact paths.
```

### Who It Is For

- people using agents for admin flows or desktop tasks
- users who want visibility into the process, not just the final answer
- teams that need a reviewable handoff package

### Platform Support

- Windows: screenshots, recording, and redaction have been locally validated
- macOS: screenshots and recording are implemented
- Linux: screenshots and recording are implemented

See also:
- [support-matrix.md](support-matrix.md)
- [known-limitations.md](known-limitations.md)

### Verify Downloads

The release includes `SHA256SUMS.txt` for verifying the wheel and source archive.
