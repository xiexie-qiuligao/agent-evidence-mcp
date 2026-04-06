# Recipes

This file contains high-signal prompt patterns for using Task Evidence MCP well.

## Long Browser Task

```text
Complete this browser-based task from start to finish.
Use the task-evidence MCP server.
Start a session named "admin-settings-rollout".
Capture a checkpoint at the initial state, after each major page transition,
after each successful submit, and on any error dialog.
Prefer screenshots over recording.
At the end, stop and return the session directory, summary path, and the key checkpoints.
```

## Debugging An Intermittent UI Failure

```text
Use the task-evidence MCP server while investigating this UI bug.
Start a session named "ui-failure-debug".
Capture checkpoints before the repro, when the failure appears, and after each retry.
If the issue depends on motion or a transient animation, use a short recording only for that step.
End with a timeline of what was observed and where the artifacts were saved.
```

## Data Entry Or Admin Workflow

```text
Perform the workflow carefully and keep a reviewable artifact trail.
Use task-evidence tools.
Start a session named "vendor-onboarding".
Capture a checkpoint after login, after each completed form section, after final submission,
and any time validation errors appear.
Save everything in the session directory and report the final artifact paths.
```

## Demo Clip For A Specific Step

```text
Use the task-evidence MCP server for this flow.
Start a session named "drag-and-drop-demo".
Capture screenshots for the setup and final state.
For the drag-and-drop interaction itself, start a short recording, stop it immediately after the step,
and include the recording path in the final summary.
```

## OCR-Ready Review

```text
Use the task-evidence MCP server for this review flow.
Capture checkpoints at the important screens.
If a screenshot contains important visible text, attach a short note explaining why it matters
and store OCR text for the artifact so the final summary is easier to search and review.
End with the session directory and summary path.
```

## Compare Two Checkpoints

```text
Use the task-evidence MCP server for this long task review.
After the workflow finishes, compare the two most important checkpoints from the same session.
Use compare_artifacts and report the verdict, changed fields, and review focus.
If OCR or notes exist, use them to explain whether the user-visible state truly changed
or whether only checkpoint metadata changed.
```

## Review The Latest Two Comparable Artifacts

```text
Use the task-evidence MCP server for this task and leave a clean review trail.
When the workflow ends, call compare_latest_artifacts for the session.
Prefer screenshots unless the latest useful evidence is a recording.
Report the verdict, changed fields, and review focus so I can quickly understand
whether the final state truly changed or only the evidence metadata changed.
```

## Create A Shareable Redacted Copy

```text
Use the task-evidence MCP server for this workflow.
When a screenshot contains sensitive text, tokens, or personal data, keep the original artifact,
then create a redacted copy before presenting results back to me.
Use redact_artifact with one or more rectangular regions and clearly report which artifact is the safe shareable copy.
Do not replace or delete the original screenshot unless I explicitly ask for that.
```
