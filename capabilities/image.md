# Image Generation Capability

Resolve the selected model locally without login/network:

```bash
python "<skill_path>/scripts/generate.py" --action image-models --model "Nano Banana V2"
```

Use the selected profile's defaults and constraints. Read only its section in [the current image catalog](../references/image-model-catalog.md) for additional detail; load the full catalog only for comparisons.

- Use generate_type=3 for text-to-image, 4 for image-to-image. Image mode requires images[] with at least one uploaded URL. Preserve the entire prompt.
- Show model names and submit numeric IDs. Default remains Nano Banana V2 (72). Image Kling O1 is 38; video Kling O1 is 92.
- Do not require every generic parameter. Banana V1 omits resolution; Flux sends empty resolution; Seedream 4.0 sends empty ratio. GPT Image 2 now uses resolution and moition_range (quality).
- Choose a resolution supported by the model and mode. Seedream 5.0 Lite accepts only 2K/3K, Pro only 1K/2K. Do not silently change explicit selections.
- Price and generate using the same normalized body. scripts/image_catalog.py validates before network access, including before balance queries.
- Inspect without login/network: `python "<skill_path>/scripts/generate.py" --action image-models`. Filter with `--model "GPT Image 2.5 Sunburst"`.
- Use [request templates](request-templates.md), [upload rules](upload.md) and the existing price/confirmation/watch workflow.
