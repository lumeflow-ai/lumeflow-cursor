# Current image model catalog

Verified 2026-09-30 against [DVQTaBJ-.js](https://www.lumeflow.ai/app/_nuxt/DVQTaBJ-.js), [text page](https://www.lumeflow.ai/app/_nuxt/Cbk-dWxW.js), [image page](https://www.lumeflow.ai/app/_nuxt/DIFnJwfA.js) and [upload component](https://www.lumeflow.ai/app/_nuxt/CZbNhc0R.js). Rules implement frontend compatibility; live backend availability has not been tested. Executable rules: [image_catalog.py](../scripts/image_catalog.py).

## Model IDs and constraints

Text mode = generate_type=3; image mode = 4. Outputs are integers 1-4. Prompt limits below are text/image characters; prompts are rejected if too long, never truncated. Reference counts apply to images[] in image mode.

| Website key | ID | Class | Resolution | Prompt limit text/image | Reference images | Modes |
|---|---:|---|---|---|---|---|
| nanobanana | 18 | Ce | omitted | 1500 / 2000 | 1-5 | text / image |
| nanobanana2 | 72 | Ce | 1K, 2K, 4K | 5000 / 5000 | 1-14 | text / image |
| nanobananaPro | 37 | Ce | text: 2K, 4K; image: 1K, 2K, 4K | 1500 / 2000 | 1-5 | text / image |
| seedream4.0 | 12 | Re | 1K, 2K, 4K | 600 / 600 | 1-10 | text / image |
| seedream5.0 | 80 | Re | 2K, 3K | 2000 / 2000 | 1-14 | text / image |
| seedream5Pro | 165 | Re | 1K, 2K | 2000 / 2000 | 1-10 | text / image |
| klingO1 | 38 | at | 1K, 2K | unavailable / 2000 | 1-9 | image |
| fluxKontextMax | 39 | tt | empty string; no selector | 600 / 1000 | 1-10 | text / image |
| fluxKontextPro | 40 | ot | empty string; no selector | 1000 / 1000 | 1-10 | text / image |
| gptImage2 | 101 | _e | 1K, 2K, 4K | 5000 / 5000 | 1-3 | text / image |
| gptImage25 | 174 | je | 1K, 2K, 4K | 5000 / 5000 | 1-16 | text / image |
| gptImage25Sunburst (mode alias) | 175 | je | 1K, 2K, 4K | 5000 / 5000 | 1-16 | text / image |

GPT Image 2.5 has modes 174=Flare and 175=Sunburst. Default gptImage25 resolves to 174; retain explicit 175 when submitting. The page's history lookup maps 175 to the gptImage25 family; it does not override new Sunburst requests. Legacy 108 resolves to Nano Banana V2 (72).

Kling O1 is excluded from the current text page selector and has no text price table; use image mode. Nano Banana Pro and Flux may be hidden in current selectors, but their definitions remain in this bundle. Flux image rules come from shared classes. These entries do not guarantee account access.

## Ratios and defaults

- Common seven ratios: 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3. Banana Pro and Flux use these; default 1:1.
- Banana V1 uses the common seven in image mode; text also allows 21:9. Default 1:1; omit resolution entirely.
- Banana V2 adds auto, 5:4 and 4:5; default auto/1K. The frontend's 4:5 option has an inconsistent label/value of 5:4; use the intended ratio key 4:5 instead of silently converting it.
- Seedream 4.0 has no ratio selector and sends ratio="". Default 1K. Its shared class sends is_web_search=0; web search is not selectable.
- Seedream 5.0 Lite/Pro and Kling O1 add 21:9. Seedream defaults 16:9 (Lite=2K, Pro=1K); Kling defaults 1:1/1K.
- GPT Image 2 adds 21:9 and 9:21, but no auto. Default 16:9/1K.
- GPT Image 2.5 uses auto plus the common seven; default auto/1K. It does not inherit GPT Image 2's 21:9/9:21 options.
- Banana Pro defaults to 2K for text and 1K for image. Flux retains resolution="" from toPlain; do not invent a selector.

## Conditional API fields

- All models: model_type, generate_type, prompt, outputs and model-specific ratio/resolution. images[] is required only in image mode. These models do not use image/image_tail or Omni video/audio arrays.
- GPT Image 2 / 2.5: moition_range="2" (low/default), "3" (medium), "4" (high). This is quality, not motion. The frontend motionRange maps to the API's exact spelling moition_range.
- Seedream 5.0 Lite: is_web_search=0 or 1 (default 0). Pro omits it. Do not copy web search to other families.
- Video-only fields, style, cfg_scale and unsupported quality fields are removed by normalization. Preserve additional API metadata such as inspiration_id.
- Model names and website keys can be passed as model_type; the image catalog resolves independently from video. Image klingO1=38; video klingo1=92.

Model-switch logic sometimes truncates existing prompts (Banana V2 to 2000, Kling to 1500). Active form components specify 5000 and 2000 respectively. Follow form limits and preserve prompts; do not reproduce destructive model-switch truncation.

## Upload constraints and inspection

Use `--action upload-image --model-kind image --model "gptImage25" --file <path>` to apply image model limits. GPT Image 2/2.5 allow 5 MiB per reference; others use the component default 10 MiB. JPG/JPEG/PNG/WebP remain supported. The frontend requires both dimensions >=300px and resizes images with either dimension above 4000px. Local upload validates format/size; it does not inspect dimensions or resize. URL count checks do not inspect remote pixels.

List without login/network: `python <skill_path>/scripts/generate.py --action image-models`. Filter with `--model "GPT Image 2.5 Sunburst"` or numeric ID.
