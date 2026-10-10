# File Upload Reference (Image / Video / Audio)

All upload operations use the same endpoint: `POST /api/lumeflow/claw-upload-image`
The script auto-detects file type and validates format + size before uploading.

`<skill_path>` = absolute directory containing `SKILL.md`.

## Supported Formats & Limits

| Type | Formats | Max Size |
|------|---------|----------|
| Image | `jpg`, `jpeg`, `png`, `webp` | 10MB |
| Video | `mp4`, `mov`, `avi`, `webm`, `mkv` | 200MB |
| Audio | `mp3`, `wav`, `m4a`, `aac`, `ogg`, `flac`, `wma` | 50MB |

These are generic upload caps, not per-model generation limits. Inspect the selected model profile with the filtered local catalog command before model-aware upload; read only its section in the [current video catalog](../references/video-model-catalog.md) if needed. Model-aware image upload extends the generic cap to 30 MiB for MiniMax H3 (also HEIC/HEIF), or Seedance 2.5 Omni. Frame mode for Seedance 2.5 remains 10 MiB. Validate available file metadata against model-specific dimensions, counts and combined size/duration limits; do not guess remote URL metadata.

```bash
python "<skill_path>/scripts/generate.py" --action upload-image --model minimaxH3 --file /path/to/image.heic
python "<skill_path>/scripts/generate.py" --action upload-image --model seedance2.5 --function-mode 1 --file /path/to/reference.png
```

## Upload Commands

**Image:**
```bash
python "<skill_path>/scripts/generate.py" --action upload-image --file /path/to/image.png
```

**Video:**
```bash
python "<skill_path>/scripts/generate.py" --action upload-video --file /path/to/video.mp4
```

**Audio:**
```bash
python "<skill_path>/scripts/generate.py" --action upload-audio --file /path/to/audio.mp3
```

**Multiple files** (e.g. `images[]` for Seedance 2.0 Omni or image-to-image): upload each one separately, collect all URLs.

## Response

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "url": "https://lac-static.imyfone.com/lumeflow_web/mobile_image/xxx.png"
    }
}
```

Use `data.url` as the value for the corresponding API field (`image`, `image_tail`, `images[]`, etc.).

## `media://` Path Resolution

In Codex or Cursor, use the attachment's actual accessible local file path with `--file`, quoted when it contains spaces. Do not convert attachments into `media://` URIs or search OpenClaw folders for ordinary local files. If only a remote URL is provided, use it directly in the request when the selected model accepts it. If an attachment has no accessible path or URL, ask for the missing input.

When the file path starts with `media://`, it is an OpenClaw platform URI — **not** a local filesystem path. The `generate.py` script will attempt to resolve it automatically. If it fails, search for the file by its filename in:

- `~/.openclaw/media/inbound/`
- `~/.openclaw/media/`
- `~/.openclaw/workspace/`
- Current working directory and subdirectories

Example: `media://inbound/1777288191014_xxx.jpg` → search for `1777288191014_xxx.jpg` in the directories above.

## Upload Rules

- The generation API only accepts remote URLs — passing a local file path directly will fail.
- Upload MUST complete before proceeding to price query or generation.
- Do NOT analyze file content or build parameter tables before upload completes.

## Image generation model context

Pass `--model-kind image --model <image name or ID>` to upload-image. GPT Image 2/2.5 allow 5 MiB per image; other current image models use 10 MiB. Example: `python "<skill_path>/scripts/generate.py" --action upload-image --model-kind image --model gptImage25 --file <path>`.

Default model-kind remains video for existing Seedance/H3 commands. Image Kling O1 uses 38, video Kling O1 uses 92. See [image catalog](../references/image-model-catalog.md) for reference counts and frontend pixel rules.
