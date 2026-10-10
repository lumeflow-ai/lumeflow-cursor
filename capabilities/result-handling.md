# Watch Results and Recovery

`<skill_path>` is the absolute directory containing SKILL.md. Watch submits once and polls every 8 seconds in Python, for up to 600 seconds by default. It returns task IDs, status, extracted URLs, cost/balance and error fields. The complete request remains in the local task store; `--debug` adds poll diagnostics, the full stored task and raw response. Do not enable it during ordinary generation.

## Completed

Present results using [rules.md](rules.md). When URL extraction succeeds, no raw response is needed. If a completed result has no extracted URL, `raw_query_response` remains available for recovery:

- Video primary: `data[*].digital_video`; cover: `cover_url`.
- Image primary: `data[*].origin_thumbnail` or `data[*].images[*].origin_thumbnail`; image fields may also contain usable results.

If primary URLs are absent, query the existing task IDs once and inspect the relevant result fields. Follow rules.md for presentation; do not fabricate links or show watermark-only links. If there is still no primary URL, explain that the task completed but a downloadable primary URL is unavailable and link to https://www.lumeflow.ai/app/mycreations/.

## Still processing

For execution tools with a hard timeout, set `--poll-timeout` below that limit (for a 120-second limit, use 100). Tools that return a running-session handle should be resumed using that handle; a tool yield does not mean the script timed out. Do not kill and resubmit a running watch.

When watch actually returns `status: processing`:

1. Keep the existing `task_ids`; never submit generation again to resume polling.
2. Wait about 30 seconds and query those IDs:

```bash
python "<skill_path>/scripts/generate.py" --action image-query --ids TASK_IDS
# For videos use --action video-query.
```

3. Integer statuses: 0 = processing, 1 = completed, 2/3/4 = failed. String processing/completed/finish/failed variants may also occur. Extract URLs on completion; handle failures via rules.md.
4. Stop after 10 minutes total from submission, including the initial watch. If still processing, report the task IDs and current status; do not automatically restart the budget or submit another generation. An unknown status is not completion.

Give brief progress updates when useful, without repeating unchanged API responses. Waiting and internal Python polling do not require an LLM turn per poll.

## Failed

Use returned `error_code` and `error` with the failure guidance in [rules.md](rules.md). Do not retry a paid submission automatically.
