# Video generation

Resolve the selected model locally without login/network:

```bash
python "<skill_path>/scripts/generate.py" --action models --model "Pixverse C1"
```

Use the selected profile's defaults and constraints. Read only its section in [the current model catalog](../references/video-model-catalog.md) if extra detail is needed; load the full catalog only for comparisons. Executable validation lives in scripts/model_catalog.py. For Seedance 2.0 family requests additionally read [Seedance rules](seedance.md).

- Default model remains Pixverse C1 (88): duration 5, resolution 720P, ratio 1:1, outputs 1. Fill other defaults from the selected profile, not from C1.
- Resolve names to IDs with the catalog; model_type in the script also accepts website keys and readable labels. Present readable model names to the user. Do not expose JS class names in generation summaries.
- Text-to-video uses generate_type=0; image/reference-to-video uses generate_type=1. Infer the mode from intent and available media; some models support only one of these.
- Do not assume every model accepts duration, resolution, ratio, motion_mode, sound, seed or an end frame. Vidu Q1 omits duration/resolution, Hailuo omits ratio, Veo omits resolution, and Happy Horse uses images[]. Follow the catalog and [templates](request-templates.md).
- Seedance 2.0/2.5 and MiniMax H3 support function_mode=0 (first/end frame) or 1 (Omni). Gemini Omni uses a single-image class and has no such reference mode. Select by intent; multiple images, video or supported audio references require Omni, except Happy Horse's images[] mode.
- Recompute valid options whenever the model, mode, duration or resolution changes. HD does not imply 1080P if the chosen model/mode lacks that resolution. Show only applicable parameters and model-specific choices in the summary.
- The script normalizes the same copied request for pricing and submission before signing, resolves legacy aliases, preserves full prompt text and stores the normalized watch body. Continue using the existing price/confirmation/watch workflow.
- Upload files to remote URLs before building the generation request. Validate local metadata against the selected model's upload limits where available; see [upload](upload.md). Do not guess missing remote metadata.
