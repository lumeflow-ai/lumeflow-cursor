# Generation Workflow

Use the absolute directory containing SKILL.md as `<skill_path>`. All API operations use `python "<skill_path>/scripts/generate.py"`; quote paths containing spaces. Python 3.10+ and network access are required. On macOS/Linux use `python3` if `python` is unavailable. The script loads private product config; never inspect or print private config files. Keep generated requests in the current workspace or an OS temporary directory, outside the installed skill/plugin directory.

## 1. Prepare inputs and request

- Upload local files and `media://` inputs before building the request or querying price; read [upload.md](upload.md) when needed.
- Resolve the selected model's supported fields/defaults via the filtered catalog command in [video.md](video.md) or [image.md](image.md). Ask only for missing information that cannot be inferred safely.
- Preserve the entire prompt and save the request once as UTF-8 JSON with a unique filename per task, for example `scratch/req-<unique-id>.json`. `scripts/write_body.py` can read JSON from stdin and returns a unique temporary file path when `--out-file` is omitted. Reuse that returned path for the quote and submission. See [request-templates.md](request-templates.md) only for the selected mode's template or unusual fields.
- No separate parameter confirmation is required before the read-only price query. Summaries follow [parameter-flow.md](parameter-flow.md).

## 2. Quote and confirm

Query with the prepared request:

```bash
python "<skill_path>/scripts/generate.py" --action video-price --body-file scratch/req-<unique-id>.json
# For images use --action image-price.
```

Show the applicable parameters, estimated time, and `data.integral` cost together. Include non-empty `data.other_discount` options. Wait for explicit confirmation of this quote before submitting a paid generation. If parameters change, update the same request file, re-query price and obtain confirmation of the new quote.

If balance is insufficient, explain it, open https://www.lumeflow.ai/app/pricing/ using the available browser tool or platform opener, and stop before generation.

## 3. Generate and wait

Reuse the exact request file from the confirmed price query:

```bash
python "<skill_path>/scripts/generate.py" --action watch-video --body-file scratch/req-<unique-id>.json
# For images use --action watch-image.
```

Do not use submit-only `--action video` / `--action image`. Watch submits once, persists the full request locally, then polls in Python. Default output is compact; use `--debug` only to investigate a problem. Read [result-handling.md](result-handling.md) for timeout recovery and failures. Brief progress updates are allowed; do not repeat parameter tables or raw poll responses.

## 4. Present result

Follow [rules.md](rules.md). Use `integral_remaining` when returned; call `--action balance` only when it is missing or the user requests a refreshed balance. Do not repeat results after a balance check.

## Authentication recovery

If API credentials are missing or an API request returns 401/403, run `python "<skill_path>/scripts/login.py"` in the foreground. Forward the login URL emitted on stderr, wait for success, then resume the original operation. Do not inspect or expose the saved credentials, split login into manual steps, or ask the user to confirm login separately.

## Task history (only on request)

```bash
python "<skill_path>/scripts/generate.py" --action tasks --status completed --limit 10
```

Show task status and download links using [rules.md](rules.md). Do not fetch history as a routine generation step.
