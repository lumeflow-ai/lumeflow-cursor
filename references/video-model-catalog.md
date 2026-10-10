# Current video model catalog

Verified 2026-09-30 from [Brr45L3F.js](https://www.lumeflow.ai/app/_nuxt/Brr45L3F.js), [text page adapter](https://www.lumeflow.ai/app/_nuxt/CrpRpg_y.js) and [image page adapter](https://www.lumeflow.ai/app/_nuxt/BD7uGgsk.js). The catalog covers all 37 website model keys. Frontend compatibility is implemented; live backend generation availability is not verified.

Executable rules: [model_catalog.py](../scripts/model_catalog.py). Inspect without login/network using `python <skill_path>/scripts/generate.py --action models`, or filter with `--model "seedance2.5"`. The result includes mode-specific profiles, defaults, ratios, audio and reference counts. `model_type` in video request bodies accepts the website key, readable model name or numeric ID; the script submits numeric IDs.

## Model directory

Audio: on/off = fixed, optional = 0/1 selectable, omit = do not send is_switch_audio. Omitted duration/resolution means the request class does not send that field; do not fill generic values. Legacy Kling versions have no resolution selector but send an internal 720P default.

| Website key | ID | Model label | JS class | Duration (seconds) | Resolution | Modes | Audio |
|---|---:|---|---|---|---|---|---|
| `kling1.6` | 1 | Kling 1.6 | Ae | 5, 10 | internal 720P; no selector | text / image | on |
| `kling2.0` | 7 | Kling 2.0 | Ae | 5, 10 | internal 720P; no selector | text / image | on |
| `kling2.5` | 19 | Kling 2.5 | Ae | 5, 10 | internal 720P; no selector | text / image | on |
| `pix6` | 21 | LumeFlow 4.0 | Fe | 2-15 (integer) | 360P, 540P, 720P, 1080P | text / image | optional |
| `pix5` | 9 | LumeFlow 3.0 | Fe | 5, 8 | 360P, 540P, 720P, 1080P | text / image | optional |
| `pix4.5` | 41 | Pixverse V5 (pix4.5) | Fe | 5, 8 | 360P, 540P, 720P, 1080P | text / image | optional |
| `hailuo02` | 3 | Hailuo 02 | qt | 6, 10 | 768P, 1080P | text / image | off |
| `veo3.1` | 4 | Google Veo 3.1 | Zt | 8 | omitted | text / image | on |
| `veo3fast` | 5 | Google Veo 3.1 Fast | Zt | 8 | omitted | text / image | on |
| `viduQ1` | 6 | Vidu Q1 | _t | omitted | omitted | text / image | off |
| `sora2` | 11 | Sora 2 | vt | 10, 15 | 720P | text / image | on |
| `venus` | 15 | Venus AI 1.0 | uo | 5, 10 | 480P, 720P, 1080P | text / image | optional |
| `sora2Pro` | 27 | Sora 2 Pro | vt | 10, 15, 25 | 1080P | text / image | on |
| `viduQ2` | 26 | Vidu Q2 | _t | 5, 10 | 540P, 720P, 1080P | text | off |
| `pix5.5` | 28 | Pixverse V5.5 | Fe | 5, 8, 10 | 360P, 540P, 720P, 1080P | text / image | optional |
| `kling2.6` | 91 | Kling 2.6 | Ae | 5, 10 | internal 720P; no selector | text / image | optional |
| `kling3.0` | 65 | Kling 3.0 | Ae | 3-15 (integer) | 720P, 1080P, 4K | text / image | optional |
| `seedance2.0` | 73 | Seedance 2.0 | Xe | 4-15 (integer) | 480P, 720P, 1080P | text / image | on |
| `seedance2.0 fast` | 71 | Seedance 2.0 Fast | Ye | 4-15 (integer) | 480P, 720P | text / image | on |
| `seedance2.0 vip` | 86 | Seedance 2.0 VIP | ke | 4-15 (integer) | 480P, 720P, 1080P | text / image | optional |
| `seedance2.0 vip fast` | 87 | Seedance 2.0 VIP Fast | Ee | 4-15 (integer) | 480P, 720P | text / image | optional |
| `klingo1` | 92 | Kling O1 | Ae | 5, 10 | internal 720P; no selector | text / image | on |
| `hailuo2.3` | 23 | Hailuo 2.3 | qt | 6, 10 | 768P, 1080P | text / image | off |
| `hailuo2.3 fast` | 25 | Hailuo 2.3 Fast | qt | 6, 10 | 768P, 1080P | text / image | off |
| `wan2.5` | 63 | Wan 2.5 | ot | 5, 10 | 480P, 720P, 1080P | text / image | on |
| `viduQ2 turbo` | 24 | Vidu Q2 Turbo | _t | 5, 10 | 540P, 720P, 1080P | image | off |
| `wan2.6` | 64 | Wan 2.6 | ot | 2-15 (integer) | 720P, 1080P | text / image | on |
| `wan2.7` | 89 | Wan 2.7 | ot | 2-15 (integer) | 720P, 1080P | text / image | on |
| `seeance1.5pro` | 50 | Seedance 1.5 Pro | ro | 4-12 (integer) | 480P, 720P, 1080P | text / image | optional |
| `pixC1` | 88 | Pixverse C1 | Fe | 2-15 (integer) | 360P, 540P, 720P, 1080P | text / image | optional |
| `wanHappyHorse1.1` | 151 | Happy Horse 1.1 | eo | 3-15 (integer) | 720P, 1080P | text / image | omit |
| `wanHappyHorse` | 104 | Happy Horse 1.0 | eo | 3-15 (integer) | 720P, 1080P | text / image | omit |
| `grok_imagine1.5` | 95 | Grok Imagine 1.5 | lu | 10, 15 | 720P | image | on |
| `seedance2.5` | 168 | Seedance 2.5 | Le | 4-30 (integer) | 480P, 720P | text / image | optional |
| `seedance2.0 mini` | 150 | Seedance 2.0 Mini | je | 4-15 (integer) | 480P, 720P | text / image | on |
| `gemini_omni` | 112 | Gemini Omni | hi | 6, 8, 10 | 720P, 1080P | text / image | on |
| `minimaxH3` | 166 | MiniMax H3 | Me | 4-15 (integer) | 768P, 2K | text / image | on |

## Request rules by family

- All catalog models require a non-empty prompt and outputs 1-4. Use model-aware defaults from the profile. Keep the full prompt unchanged and quote price with the same request body used for generation.
- Text mode is generate_type=0; image mode is generate_type=1. Vidu Q2 (26) is text-only in the current page adapter; Vidu Q2 Turbo (24) and Grok Imagine 1.5 (95) are image-only. Do not route those to unsupported modes. Video-to-video remains outside this Skill's generation workflow.
- Prompt limits: ordinary models 2000 characters; Kling ordinary image mode 2500 and Kling 3.0 all modes 2500; Grok 4000; pix6/pixC1, Wan 2.7, Happy Horse, Seedance 2.0/2.5 and MiniMax H3 5000.
- Kling 2.6 uses 91; Kling O1 uses 92. Existing numeric IDs 29/30 are retained as legacy requests, but are not automatically remapped because the website's On map does not assert that equivalence. Kling 2.0 is included via the shared Ae class even though current selectors may hide it.
- Kling 3.0 uses integer durations 3-15 and 720P/1080P/4K. Its price table contains 1/2-second rows, but the active UI lists start at 3; follow the active UI. Ae legacy versions have no independent resolution selector; their toPlain includes an internal 720P default, which is preserved without inventing new resolution options.
- For ordinary Kling motion_mode, use 1=standard or 2=professional. cfg_scale is a number 0-1 (UI percentage divided by 100). O1 does not use cfg_scale/motion_mode. Image-mode Ae omits ratio. End frame is unavailable for Kling 2.6; for Kling 1.6/2.5 it is used with professional mode. Do not describe motion_mode as arbitrary motion intensity.
- pix6 is LumeFlow 4.0 (21), pix5 is LumeFlow 3.0 (9). pix4.5 is the site's historical key for the current label Pixverse V5 (41); retain the exact key/ID. Do not map Pixverse V5 to 9 based on the old Skill catalog.
- Fe models use resolutions 360P/540P/720P/1080P. For 9/41 at 8s omit 1080P; for 28 at 10s omit 1080P. pix6/pixC1 support every integer 2-15s at all four resolutions. Fe image requests omit ratio. Only 9/21/88 expose seed; only 9 retains negative_prompt. Style 0-5 is exposed by pix4.5; current pix5/pix5.5 page adapters filter style controls. Fe.toPlain retains motion_mode (default 2), even for versions whose current page does not expose a mode control.
- Hailuo 02/2.3/Fast use 6 or 10 seconds. At 6s resolution is 768P or 1080P; at 10s only 768P. Send audio=0; omit ratio, motion_mode and image_tail.
- Veo 3.1/Fast use fixed 8s, audio=1, ratio 16:9 or 9:16, and no resolution field in Zt.toPlain. Do not impose a resolution selector that the class does not define.
- Vidu Q1 uses style 0/1 for text and moition_range 1-4 (API spelling) for text/image. Omit duration/resolution; Q1.toPlain has neither. Vidu Q2 uses 5/10s, 540P/720P/1080P, ratio 4:3 or 3:4. Q2 Turbo uses an image, 5/10s, 540P/720P/1080P and moition_range 1-4; omit ratio and end frame. Do not reuse its unrelated video-to-video 5/7-second rule.
- Sora 2 supports 10/15s at 720P in the active UI; Pro supports 10/15/25s at 1080P. Both have audio=1. Text ratio 16:9/9:16; ordinary Sora image mode omits ratio, Pro retains it. The historical price table's Sora 1080P rows do not establish a current UI option.
- Venus uses 5/10s, 480P/720P/1080P, selectable audio, ratios 21:9/16:9/1:1/3:4/9:16; first/end frames supported.
- Wan 2.5 uses 5/10s and 480P/720P/1080P. At 480P text ratios are only 16:9/9:16/1:1; 720P/1080P add 4:3/3:4. Wan 2.6/2.7 use integers 2-15s and 720P/1080P. All have audio=1 and optional seed. Only 2.6 uses shot_type single/multi; default multi. Image modes omit ratio; only Wan 2.7 exposes end frame in current page state.
- Happy Horse 1.0/1.1 both use integers 3-15s (superseding the Skill's previous 2s minimum), 720P/1080P, ratios 16:9/9:16/1:1/4:3/3:4 and optional seed. Image generation uses images[] with 1-9 reference images, not image/image_tail. The script converts a legacy single image to images[]; it rejects end frame/video/audio. Omit is_switch_audio/motion_mode; eo.toPlain has no audio toggle.
- Seedance 1.5 Pro uses the website typo key seeance1.5pro (50); corrected seedance1.5pro and readable Seedance 1.5 Pro are also accepted. Durations are integers 4-12; resolutions 480P/720P/1080P; selectable audio; ratio auto/16:9/9:16/1:1/4:3/3:4/21:9. Supports first/end frame, not Omni.
- Grok Imagine 1.5 uses an image, 10/15s, 720P, audio=1, ratios Auto/2:3/3:2/1:1/9:16/16:9. Preserve capitalized Auto for this class.
- Gemini Omni uses text or a single image, 6/8/10s, 720P/1080P, ratios 16:9/9:16 and audio=1. Despite the name, hi does not implement function_mode or images/videos/audios reference arrays.
- Seedance 2.0/Fast/VIP/VIP Fast/Mini: read [Seedance 2.0 rules](../capabilities/seedance.md). All use integer 4-15s. VIP audio is selectable; ordinary/Fast/Mini audio=1. Only 73/86 offer 1080P; 71/87/150 offer 480P/720P.
- Seedance 2.5 (168) uses integers 4-30s, 480P/720P, selectable audio, prompt<=5000, outputs 1-4, ratios auto/21:9/16:9/4:3/1:1/9:16/3:4. Text, first/end-frame and Omni supported. Frame mode forces ratio auto; Omni retains duration, resolution, ratio and audio. Do not offer 1080P from another Seedance version.
- MiniMax H3 (166) uses integers 4-15s, 768P/2K, audio=1, prompt<=5000, outputs 1-4. Text and frame mode use ratio auto; Omni additionally offers 21:9/16:9/4:3/1:1/3:4/9:16. First/end-frame and Omni supported; retain duration and audio in Omni. Do not reuse Hailuo 02/2.3's resolution rules.

## Reference media limits

For Seedance 2.0 use the dedicated rules. For additional reference models:

| Model / mode | Images | Videos | Audio |
|---|---|---|---|
| Happy Horse 1.0/1.1 image mode | 1-9; each <=10 MiB, width/height >=400; page upload normalizes to JPG | None | None |
| Seedance 2.5 Omni | Up to 30; each <=30 MiB, width/height >=300; image total <=64 MiB | Up to 10; each <=200 MiB; width/height 640-1920; total duration <=30s | Up to 10; each <=15 MiB; each duration 2-30s; total <=64 MiB and <=30s |
| MiniMax H3 Omni | Up to 9; each <=30 MiB, width/height >=300; JPG/JPEG/PNG/WebP/HEIC/HEIF | Up to 3; each <=50 MiB; total duration <=15s; no explicit dimensions in this override | Up to 3; each <=30 MiB; each duration 2-15s; total <=90 MiB and <=15s |
| MiniMax H3 first/end frame | Each <=30 MiB, width/height >=300; JPG/JPEG/PNG/WebP/HEIC/HEIF | None | None |

At least one reference material is required overall in Omni; do not require images if supported video/audio references exist. The script validates reference array types/counts; URL metadata cannot be verified locally. Check available local file metadata before upload and do not invent remote dimensions, sizes or durations. Default image uploader supports 10 MiB JPG/JPEG/PNG/WebP; use --model minimaxH3 for 30 MiB/HEIC/HEIF or --model seedance2.5 --function-mode 1 for 30 MiB Omni images. Seedance 2.5 frame uploads retain the default 10 MiB component limit.

## Legacy mappings and availability

Website aliases: 70/74/76/160 ->71, 161->73, 152/153->150, 130->21, 32->64, 22->63. Do not infer additional numeric remaps. Unknown custom numeric IDs retain the existing generic behavior; they are outside this verified directory.

Catalog membership and valid local request shape do not guarantee account access, regional availability, pricing or successful generation. Query the existing price endpoint, follow the existing confirmation workflow and submit with watch-video. Do not introduce frontend subscription locks into the Skill; the API determines account access. Reuse the quoted request body; use price endpoint results instead of guessed frontend coin estimates.
