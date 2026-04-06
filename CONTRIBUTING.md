# Contributing

Thanks for contributing to Agent Evidence MCP.

## Development Flow

1. Create a focused branch for your change.
2. Install the project in editable mode:

```bash
pip install -e .
```

3. Run the test suite before opening a PR:

```bash
python -m pytest -q
```

4. If you touch packaging or release behavior, also confirm the project still builds:

```bash
python -m build --sdist --wheel
```

## What Good Contributions Look Like

- keep the screenshot-first workflow stable
- make recording optional rather than mandatory
- preserve predictable artifact paths and session structure
- improve user-facing errors when behavior changes
- add or update tests alongside behavior changes

## Before Opening A PR

- confirm README examples still match real commands
- confirm new tools or flags are documented
- confirm existing sessions and summaries still behave sensibly
- confirm CI would still pass on both Windows and Linux
- update `CHANGELOG.md` for user-facing changes

## Scope Guidance

High-value contributions include:

- platform support improvements
- better artifact summaries
- clearer MCP client examples
- OCR or redaction hooks
- recording reliability improvements
