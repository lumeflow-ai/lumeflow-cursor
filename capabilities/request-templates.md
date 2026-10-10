# Request Body Templates

`<skill_path>` = absolute directory containing `SKILL.md`.

## Prompt Integrity

The `prompt` field MUST contain the ENTIRE, exact text of the optimized prompt (including all formatting like `[Title]`, `[00:00-00:03] Shot 1`, etc.). Do NOT truncate, summarize, or remove formatting. The downstream model requires the FULL text to generate correctly.

**Handling Long/Multi-line Prompts**: If the prompt is long and contains newlines (like Seedance prompts), do **not** pass it via `--body '...'` inline on the command line because escaping quotes and newlines in PowerShell usually fails or causes truncation. Instead:
1. Use an available file-writing tool, or feed JSON to `scripts/write_body.py` through stdin, to save the complete JSON request body to a unique temporary file (e.g., `scratch/req-<unique-id>.json`).
2. Run the script using `--body-file` instead of `--body`:
   `python "<skill_path>/scripts/generate.py" --action video-price --body-file scratch/req-<unique-id>.json`

## Templates

These are mode-specific examples, not universal schemas. Inspect the selected model profile with the filtered local catalog command before copying a template; read only its catalog section if needed. Unsupported fields are omitted or rejected by scripts/model_catalog.py. Resolve model-specific duration, resolution, audio, ratios and reference limits first.

**Text-to-video** (generate_type = `0`):
```json
{"generate_type":0,"model_type":88,"prompt":"{prompt}","is_switch_audio":1,"ratio":"1:1","duration":5,"resolution":"720P","motion_mode":"2","outputs":1}
```

**Image-to-video** (generate_type = `1`):
```json
{"generate_type":1,"model_type":88,"prompt":"{prompt}","is_switch_audio":1,"ratio":"1:1","duration":5,"resolution":"720P","motion_mode":"2","outputs":1,"image":"{image}","image_tail":""}
```

**Seedance family text-to-video** (IDs 73, 71, 86, 87, 150):
```json
{"generate_type":0,"model_type":71,"prompt":"{prompt}","ratio":"auto","duration":5,"resolution":"480P","outputs":1,"is_switch_audio":1}
```

**Seedance family first/last-frame**:
```json
{"generate_type":1,"model_type":73,"function_mode":0,"prompt":"{prompt}","ratio":"16:9","duration":5,"resolution":"720P","outputs":1,"is_switch_audio":1,"image":"{image_url}","image_tail":""}
```

**Seedance family Omni** (73/71: images/videos; 86/87/150 also support audios):
```json
{"generate_type":1,"model_type":150,"function_mode":1,"prompt":"{prompt}","ratio":"auto","duration":5,"resolution":"720P","outputs":1,"is_switch_audio":1,"images":["{image_url}"],"videos":[],"audios":[]}
```
Keep duration and is_switch_audio in Omni; omit image/image_tail and motion_mode. Omit audios for 73/71. At least one reference material is required overall. Fast and Mini allow only 480P/720P; 73/86 also allow 1080P. VIP permits is_switch_audio=0. See [Seedance rules](seedance.md).

**Seedance 2.5 Omni** (4-30s, 480P/720P, selectable audio):
```json
{"generate_type":1,"model_type":168,"function_mode":1,"prompt":"{prompt}","ratio":"16:9","duration":20,"resolution":"720P","outputs":1,"is_switch_audio":0,"images":["{image_url}"],"videos":[],"audios":[]}
```

**MiniMax H3 first/end-frame** (4-15s, 768P/2K, auto ratio, audio=1):
```json
{"generate_type":1,"model_type":166,"function_mode":0,"prompt":"{prompt}","ratio":"auto","duration":5,"resolution":"768P","outputs":1,"is_switch_audio":1,"image":"{image_url}","image_tail":""}
```
For H3 Omni use function_mode=1 and images/videos/audios instead of image/image_tail; retain duration, ratio, resolution, outputs and audio. See catalog for upload limits.

**Happy Horse multi-image reference** (104 or 151):
```json
{"generate_type":1,"model_type":151,"prompt":"{prompt}","ratio":"16:9","duration":5,"resolution":"720P","outputs":1,"images":["{image_url_1}","{image_url_2}"]}
```
Do not add audio, motion_mode, function_mode or image_tail.

**Vidu Q1** (no duration/resolution fields):
```json
{"generate_type":0,"model_type":6,"prompt":"{prompt}","ratio":"1:1","outputs":1,"is_switch_audio":0,"style":"0","moition_range":"1"}
```
For Q1 image mode use generate_type=1 and image; omit ratio and style. moition_range is the API spelling. Q2 text mode and Q2 Turbo image mode instead include duration (5/10) and resolution (540P/720P/1080P).

**Grok Imagine 1.5 image-to-video**:
```json
{"generate_type":1,"model_type":95,"prompt":"{prompt}","ratio":"Auto","duration":10,"resolution":"720P","outputs":1,"is_switch_audio":1,"image":"{image_url}"}
```

**Veo 3.1 text-to-video** (no resolution field):
```json
{"generate_type":0,"model_type":4,"prompt":"{prompt}","ratio":"16:9","duration":8,"outputs":1,"is_switch_audio":1}
```

**Text-to-image** (generate_type = `3`):
```json
{"generate_type":3,"model_type":72,"prompt":"{prompt}","ratio":"auto","resolution":"1K","outputs":1}
```

**Image-to-image** (generate_type = `4`):
```json
{"generate_type":4,"model_type":72,"prompt":"{prompt}","ratio":"auto","resolution":"1K","outputs":1,"images":["{image_url_1}"]}
```

**GPT Image 2.5 Sunburst image-to-image** (174 for Flare):
```json
{"generate_type":4,"model_type":175,"prompt":"{prompt}","ratio":"auto","resolution":"2K","moition_range":"3","outputs":1,"images":["{image_url}"]}
```

**Seedream 5.0 Lite text-to-image with web search**:
```json
{"generate_type":3,"model_type":80,"prompt":"{prompt}","ratio":"16:9","resolution":"2K","is_web_search":1,"outputs":1}
```

**Kling O1 image-to-image** (image ID 38):
```json
{"generate_type":4,"model_type":38,"prompt":"{prompt}","ratio":"1:1","resolution":"1K","outputs":1,"images":["{image_url}"]}
```

For other image models, inspect their filtered profile or the relevant section of [the current image catalog](../references/image-model-catalog.md). Banana V1 omits resolution; Flux sends empty resolution; Seedream 4.0 sends empty ratio. GPT Image 2 uses moition_range and resolution.

## Verification Checklist

Use only if you cannot copy the price query body verbatim:
- **Video**: model_type, generate_type, full prompt, outputs and the conditional fields defined in the current catalog; do not copy every field from the generic C1 example. In particular Q1 has no duration/resolution, Veo has no resolution, Happy Horse uses images[], and image modes may omit ratio.
- **Video (Seedance family)**: generate_type, model_type, prompt, ratio, duration, resolution, outputs, is_switch_audio; first/last-frame adds function_mode=0 and image/image_tail; Omni adds function_mode=1 and images/videos (audios only for 86/87/150). Do not include motion_mode.
- **Image**: `generate_type`, `model_type`, `prompt`, `ratio`, `resolution`, `outputs` (and `images` if image-to-image)
