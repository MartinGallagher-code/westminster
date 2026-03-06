---
name: publish
description: Commit current changes, merge into main, and push to remote. Use when the user wants to publish, deploy, or ship their work.
disable-model-invocation: true
allowed-tools: Bash
---

The user has invoked /publish, which means they have already authorized the full publish workflow. Do NOT use AskUserQuestion at any point. Do NOT ask for confirmation. Do NOT pause between steps. Execute all steps back-to-back automatically.

Steps:

1. **Commit** — Stage and commit all current changes on the working branch (exclude .coverage and .claude/). Write a clear, concise commit message based on the diff.
2. **Merge** — Merge the working branch into `main`. If already on `main`, skip this step.
3. **Push** — Run `git push origin main` immediately. The user has pre-authorized this action by invoking /publish.

If any step fails, stop and report the error. Otherwise, report the final commit hash and confirm the push succeeded.
