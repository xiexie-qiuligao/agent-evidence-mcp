# Release Checklist

Use this checklist before publishing a new GitHub release or Python package build.

## Product Sanity

- Confirm the README still reflects the current CLI commands and MCP tools.
- Confirm the scope still matches the product rule: capture better evidence, review evidence more effectively, or keep the user experience predictable and lightweight.
- Confirm new behavior does not make recording mandatory for screenshot-first workflows.
- Confirm privacy-related changes preserve original artifacts unless destructive behavior is explicitly intended.

## Quality

- Run `python -m pytest -q`.
- Run `python -m build --sdist --wheel`.
- If a Windows capture or recording change landed, run at least one real local validation flow.
- Confirm common failure paths still return plain-language errors.

## Docs

- Update `README.md` if commands, defaults, or examples changed.
- Update `CHANGELOG.md`.
- Update platform notes if backend behavior changed.
- Update the support matrix if platform status changed.
- Update known limitations when a caveat is added, removed, or becomes less severe.
- Add or refresh prompt examples when a workflow becomes easier or safer.

## Release Package

- Confirm `dist/` contains both sdist and wheel artifacts.
- Spot-check `agent-evidence-mcp --help`.
- Confirm the published version number matches `pyproject.toml` and the changelog entry.

## GitHub Release

- Summarize user-facing highlights first, then implementation changes.
- Call out platform limitations clearly, especially Windows-first capture support.
- Include one short example of the intended long-task workflow in the release notes.
