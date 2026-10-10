# Seedance 2.0 family

Source: https://www.lumeflow.ai/app/_nuxt/Brr45L3F.js (checked 2026-09-30; classes Xe, Ye, ke, Ee, je; catalog po, aliases On). These are current frontend rules; backend generation has not been verified.

| Model name | model_type | Resolution | Audio | Omni references |
|---|---|---|---|---|
| seedance2.0 | 73 | 480P, 720P, 1080P | Always on | images, videos |
| seedance2.0 fast | 71 | 480P, 720P | Always on | images, videos |
| seedance2.0 vip | 86 | 480P, 720P, 1080P | 0 or 1 | images, videos, audios |
| seedance2.0 vip fast | 87 | 480P, 720P | 0 or 1 | images, videos, audios |
| seedance2.0 mini | 150 | 480P, 720P | Always on | images, videos, audios |

## Common parameters

- duration: every integer from 4 to 15, default 5, including Omni.
- resolution: default 480P. Fast and Mini do not support 1080P.
- outputs: 1-4, default 1. prompt: non-empty text, at most 5000 characters. Preserve the full prompt.
- ratio: use auto by default; choices auto, 16:9, 9:16, 4:3, 3:4. VIP models additionally offer 1:1 and 21:9. Normalize Auto to auto. Ordinary classes default internally to 1:1 although their UI lists omit it; the script accepts 1:1 for compatibility.
- is_switch_audio: default 1. Always 1 for 73/71/150; allow 0 or 1 for 86/87.
- Do not send motion_mode for these models.
- Legacy IDs 70/74/76/160 map to 71; 161 maps to 73; 152/153 map to 150. Display current model IDs. The current site labels 73/71 SD2 Creative Engine / Fast; preserve explicit names and IDs to distinguish VIP channels.
- Recompute available resolution, duration, audio and reference-mode choices whenever the model changes.

## Generation modes

Text-to-video uses generate_type=0 and the common fields; no reference materials.

First/last-frame control uses generate_type=1, function_mode=0, the common fields, image (required start frame), and image_tail (optional end frame; empty if absent).

Omni uses generate_type=1, function_mode=1, the common fields **including duration and is_switch_audio**, images/videos arrays and audios for 86/87/150. At least one reference material is required overall; each array may be empty individually. Omit image, image_tail and motion_mode. Do not require images when video or supported audio references exist.

Select reference mode by intent: first/last-frame control uses mode 0; multiple images, video or audio references use mode 1. Three or more images require Omni. One or two references can also use Omni.

## Omni upload limits

| Models | Images | Videos | Audio |
|---|---|---|---|
| 73, 71 | Up to 9; each <=10 MiB, width/height >=300 | Up to 1; each <=50 MiB, width/height 640-1920 | Not supported |
| 86, 87 | Up to 9 (component fallback); size/dimensions not explicitly specified by override | Up to 3; each <=50 MiB, width/height 640-1920, combined duration <=15s | Up to 3; each <=15 MiB, duration 2-15s, combined duration <=15s |
| 150 | Up to 9; each <=10 MiB, width/height >=300 | Up to 3; each <=50 MiB, width/height 640-1920, combined duration <=15s | Up to 3; each <=15 MiB, duration 2-15s, combined duration <=15s |

Inspect local media metadata before upload where available. The script validates array types/counts and model compatibility; it cannot verify remote URL file sizes, dimensions or durations. Do not invent those values.

## Pricing

Always query video-price before generating. Frontend estimates use per-second coins times duration times outputs, with no generic bulk discount for these classes:

| ID | Text / first-last-frame rate (480P / 720P / 1080P) | Omni rate |
|---|---|---|
| 73 | 12 / 16 / 64 | 16 / 16 / 72 |
| 71 | 10 / 20 / unavailable | 14 / 20 / unavailable |
| 86 | 16 / 32 / 78 | 20 / 40 / 84 |
| 87 | 12 / 28 / unavailable | 16 / 32 / unavailable |
| 150 | 10 / 20 / unavailable | 12 / 24 / unavailable |

71 adds 2 coins per output at duration 4; 150 adds 2 coins per output only for 480P at duration 4. These estimates are informational; use the price endpoint response in the confirmation summary.
