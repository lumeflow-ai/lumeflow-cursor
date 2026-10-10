# LumeFlow for Cursor

Generate images and videos with Lumeflow using the [lumeflow-video skill](SKILL.md).

Requires a Cursor version with plugin support and local plugin imports, Python 3.10+, network access and a Lumeflow account. Use Cursor Agent mode with terminal execution enabled.

Copy the contents of this plugin package into `~/.cursor/plugins/local/lumeflow`, including the hidden `.cursor-plugin/` directory. Reload Cursor with **Developer: Reload Window**, then check **Customize**. Local plugin imports must be allowed by your organization. A marketplace installation of the same plugin takes precedence.

Ask the agent: "Use Lumeflow to generate a portrait image of an orange cat." You can also use `/lumeflow`, `/lumeflow-login` and `/lumeflow-balance`.

If using Cursor Agent CLI, load this directory with `agent --plugin-dir /absolute/path/to/lumeflow`.

When authorization is needed, the agent starts browser login and waits for completion. Credentials remain in the LumeFlow user data directory shared with Codex, outside the plugin. Generation follows upload, quote, user confirmation, submit, and wait. Read-only balance and model queries do not submit generation tasks.

Keep request files in your workspace or OS temporary directory. The plugin includes no API key, private configuration, request files, HTTP logs, or Python caches. Existing backend authentication routes and the `openclaw` platform header remain compatible; installing into Cursor does not change the backend protocol.

This package uses the root-skill discovery supported by [Cursor's plugin reference](https://cursor.com/docs/reference/plugins). See [Cursor's local testing guide](https://cursor.com/docs/plugins#test-plugins-locally) for installation details. It provides local Python scripts, not an MCP server or an automatically configured cloud execution environment.
