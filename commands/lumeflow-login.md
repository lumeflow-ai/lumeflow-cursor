---
name: lumeflow-login
description: Sign in to a Lumeflow account through the browser and save credentials privately.
---

Use [the Lumeflow skill](../SKILL.md). The plugin root is the parent of this command's directory; resolve scripts there, not in the current workspace.

Run `python "<plugin_root>/scripts/login.py"` in the foreground (or `python3` on macOS/Linux). Forward the login URL to the user and allow them to complete browser login. Resume the running terminal session until the script finishes; a tool yield does not mean login failed. Report success only when the script returns `status: success`. Do not read the private config or display credentials. Login does not submit a paid generation task.
