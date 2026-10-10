# User-facing Output

Use Markdown and the language of the user's latest message. Generation messages should be concise and readable; do not expose scripts, environment variables, JSON, API keys or error stacks.

## Quote

Show one parameter summary with estimated time and quoted credit cost; see [parameter-flow.md](parameter-flow.md). Do not repeat unchanged tables at later steps.

## Results and history

Show task ID, friendly status, one localized Markdown download link per unique URL in `result_urls`, and remaining credits when available. Do not embed previews or show `result_urls_watermark` or watermark distinctions. If only watermark URLs exist, recover a primary download URL using the query fallback in [result-handling.md](result-handling.md); never claim a usable primary URL exists if none is returned.

Example:

任务 ID：27502 · 已完成
[下载图片资源](https://example.com/result.jpeg)
剩余积分：209

## Failures

Look up returned `error_code` in the Task Failure Error Codes section of [api_reference.md](../references/api_reference.md) only on failure. Translate the matching explanation; if unavailable, use a brief generic failure message. Explain that failed tasks do not deduct credits. For code 2002, describe the sensitive-content review notice and open https://www.lumeflow.ai/app/mycreations/ so the user can check it.
