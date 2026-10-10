---
name: lumeflow-balance
description: Query the current Lumeflow credit balance without submitting a generation task.
---

Use [the Lumeflow skill](../SKILL.md) and [authentication recovery](../capabilities/workflow.md#authentication-recovery). The plugin root is the parent of this command's directory; resolve scripts there, not in the current workspace.

Run `python "<plugin_root>/scripts/generate.py" --action balance` (or `python3` on macOS/Linux). If credentials are missing or the request returns 401/403, complete browser login in the foreground and retry the balance query once. Report the returned balance in the user's language; do not invent values or display private configuration. This command does not submit a paid generation task.
