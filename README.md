# Agent Evidence MCP

[![Release](https://img.shields.io/github/v/release/xiexie-qiuligao/agent-evidence-mcp?include_prereleases&label=release)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/releases)
[![CI](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/xiexie-qiuligao/agent-evidence-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/xiexie-qiuligao/agent-evidence-mcp)](./LICENSE)

![Agent Evidence MCP hero](docs/assets/hero.svg)

## 中文

让 agent 在执行长任务时，自动留下截图、录屏、备注和总结。

Agent Evidence MCP 不是单纯的截图工具，它更适合这些场景：

- 让 agent 操作浏览器后台、桌面软件或多步骤流程
- 希望每到关键节点自动留图，出错时额外留证据
- 做完后需要一个清晰的交付目录，方便自己、同事或客户复盘

### 你装上之后能做什么

- 开一个任务会话：`start_session`
- 在关键节点截图：`capture_checkpoint`
- 必要时录一小段屏幕：`start_recording` / `stop_recording`
- 给证据加备注或 OCR 文本：`attach_note` / `ocr_artifact`
- 对敏感区域打码，生成可分享副本：`redact_artifact`
- 结束时自动拿到 `summary.md`、`timeline.jsonl` 和所有 artifact

### 最适合的使用方式

它最适合配合 agent 一起用。你不用自己手动调很多命令，通常只要告诉 agent：

```text
用 agent-evidence MCP 帮我完成这个任务。
开始前先创建一个 session。
每到关键节点截一张图，出错时额外截图。
优先截图，只有在动作过程很重要时才短录屏。
结束后把 summary 和所有关键产物路径告诉我。
```

### 3 步上手

1. 安装

```bash
pip install -e .
```

2. 初始化配置

```bash
agent-evidence-mcp init
```

3. 启动 MCP 服务

```bash
agent-evidence-mcp serve
```

### 命令行快速体验

创建一个 session：

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

截一张关键节点图：

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully."
```

结束并生成总结：

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

### 结果会保存成什么样

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

你最终拿到的不是一堆散乱截图，而是一整套有时间线、有总结、可复盘的任务证据。

### 平台支持

| 能力 | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Session / MCP / CLI | 已实现 | 已实现 | 已实现 |
| 截图 | 已实现并已本地验证 | 已实现 | 已实现 |
| 录屏 | 已实现并已本地验证 | 已实现 | 已实现 |
| Redaction | 已实现并已本地验证 | 未实现 | 未实现 |

更详细的说明见：[support-matrix.md](docs/support-matrix.md)

### 校验下载文件

release 页面会附带 `SHA256SUMS.txt`。  
如果你下载了 wheel 或源码包，可以这样校验：

```bash
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1-py3-none-any.whl SHA256
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1.tar.gz SHA256
```

### 常见使用场景

- 浏览器后台配置
- QA 回归验证
- 桌面应用操作
- 数据录入流程
- 需要 agent 留下执行证据的长期任务

### 文档

- [客户端配置](docs/client-configs.md)
- [Prompt 示例](docs/recipes.md)
- [支持矩阵](docs/support-matrix.md)
- [已知限制](docs/known-limitations.md)
- [架构说明](docs/architecture.md)
- [Examples 索引](examples/README.md)

---

## English

Let your agent leave behind screenshots, short recordings, notes, and a final summary while it works through a long-running task.

Agent Evidence MCP is not just a screenshot tool. It is built for workflows where an agent is doing real work and you want visible checkpoints plus a clean handoff package at the end.

### What You Get

- start a task session with `start_session`
- capture milestone screenshots with `capture_checkpoint`
- record short screen segments when motion matters
- attach notes or OCR text to artifacts
- generate redacted copies for safer sharing
- finish with `summary.md`, `timeline.jsonl`, and organized artifacts

### Best Way To Use It

This project is designed to work with an agent. In most cases you can simply tell the agent:

```text
Use agent-evidence MCP for this task.
Start a session first.
Capture a screenshot at each major milestone and an extra one on errors.
Prefer screenshots over recording unless motion matters.
When the task is done, give me the summary and the key artifact paths.
```

### Quick Start In 3 Steps

1. Install

```bash
pip install -e .
```

2. Initialize config

```bash
agent-evidence-mcp init
```

3. Start the MCP server

```bash
agent-evidence-mcp serve
```

### Try It From The CLI

Create a session:

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

Capture a milestone:

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully."
```

End the session:

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

### What The Output Looks Like

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

The result is not a pile of loose screenshots. It is a reviewable task record.

### Platform Support

| Capability | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Session / MCP / CLI | Implemented | Implemented | Implemented |
| Screenshots | Implemented and locally validated | Implemented | Implemented |
| Recording | Implemented and locally validated | Implemented | Implemented |
| Redaction | Implemented and locally validated | Not implemented | Not implemented |

See [support-matrix.md](docs/support-matrix.md) for more detail.

### Verify Downloads

The release includes `SHA256SUMS.txt`.  
If you download the wheel or source archive, you can verify them like this:

```bash
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1-py3-none-any.whl SHA256
certutil -hashfile dist\\agent_evidence_mcp-0.1.0a1.tar.gz SHA256
```

### Common Use Cases

- browser admin flows
- QA verification
- desktop operations
- data-entry workflows
- long-running agent tasks that need visible evidence

### Docs

- [Client configs](docs/client-configs.md)
- [Prompt recipes](docs/recipes.md)
- [Support matrix](docs/support-matrix.md)
- [Known limitations](docs/known-limitations.md)
- [Architecture](docs/architecture.md)
- [Examples index](examples/README.md)
