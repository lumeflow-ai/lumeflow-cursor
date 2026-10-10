---
name: lumeflow-video
description: >
  Generate videos and images with Lumeflow. Supports text-to-video,
  image-to-video, text-to-image, image-to-image, image & video & audio upload,
  login, and authorization.
---

# Lumeflow Generation

Generate video/image tasks through the Lumeflow API, with upload and browser login support.

Use Python 3.10+ in a local execution environment with network access. Resolve script paths from this skill's own directory, rather than the current working directory. User instructions take precedence over workflow defaults; a previous explicit authorization for the same unchanged quote is sufficient.

## Start here

For generation, read [workflow](capabilities/workflow.md) and [output rules](capabilities/rules.md) once per conversation; reuse them unless they change. Then read only [video](capabilities/video.md) or [image](capabilities/image.md) for the requested media type. Prepare inputs, query price, show parameters/time/cost, obtain one explicit quote confirmation, then submit and watch using the same request file.

Use `--action watch-video` / `--action watch-image`; submit-only `video` / `image` actions leave tasks unresolved. Missing credentials or 401/403 trigger foreground `scripts/login.py`; see workflow for recovery. Never expose API keys or private config.

## Load only when needed

- Local attachments or `media://` inputs: [upload](capabilities/upload.md); upload before request construction or price queries.
- Parameter summary: [parameter flow](capabilities/parameter-flow.md).
- Body construction: locate only the relevant mode in [request templates](capabilities/request-templates.md). Preserve the full prompt.
- Seedance 2.0 family (73/71/86/87/150; legacy 76 maps to 71): [Seedance](capabilities/seedance.md).
- Watch timeout, missing result URL or failure: [result handling](capabilities/result-handling.md).
- Model details: use filtered local catalog commands from video/image modules. Read only the selected model section of [video catalog](references/video-model-catalog.md) or [image catalog](references/image-model-catalog.md) if the command leaves a question unanswered. Full catalogs are needed only for model comparisons.
- Failure codes: relevant table in [API reference](references/api_reference.md), only on failure.

Avoid loading unrelated modes, full catalogs, historical task lists, debug logs or implementation source for ordinary generation. Keep full requests and poll diagnostics in files; return compact results to the conversation.
