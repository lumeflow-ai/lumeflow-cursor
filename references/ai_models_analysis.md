# AI Model Integration Parameter Analysis

> Generated: 2026-03-19 | Project: `memevid_web`

---

## 1. Model Overview

### Unified API Endpoints

| Category | HTTP Method | Endpoint Path |
|----------|-------------|---------------|
| Video generation (text/image/video-to-video) | POST | `/api/lumeflow/video-generate` |
| Image generation (text/image-to-image) | POST | `/api/lumeflow/image-generate` |
| AI image effects | POST | `/api/lumeflow/image-effects-generate` |

**Key discriminator fields**: model_type (numeric catalog ID) + generate_type (0/1 for this Skill video workflow; 3/4 for image).

---

## 2. Current Video Generation Models

Updated 2026-09-30 from Brr45L3F.js and the current text/image page adapters. Read [current video catalog](video-model-catalog.md) for all 37 IDs/classes, defaults, supported modes, request fields and upload limits. The original 2026-03-19 video analysis has been replaced; executable rules live in scripts/model_catalog.py. Use --action models to inspect profiles without network access.

Video modes supported by this Skill are generate_type=0 (text) and 1 (image/reference). Website video-to-video uses a separate page workflow and remains outside this Skill's generation workflow. Model-specific fields are described in the catalog; do not require duration/resolution for Vidu Q1 or motion_mode for reference models.

## 3. Image Generation Models (`/api/lumeflow/image-generate`)

Updated 2026-09-30 from DVQTaBJ-.js and current page adapters. Read [current image catalog](image-model-catalog.md) for all 11 keys and GPT Image 2.5 modes, IDs/classes, resolution, quality and reference limits. Executable rules: scripts/image_catalog.py; inspect with --action image-models.

Image modes: generate_type=3 (text), 4 (images[]). Kling O1 Image (38) is image-only. GPT Image 2/2.5 use resolution and moition_range quality; the historical no-resolution rule is superseded.

---

## 4. AI Image Effects (`/api/lumeflow/image-effects-generate`)

### 4.1 Request Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `special_id` | `number` | Yes | — | Effect ID (from effects list endpoint) |
| `images` | `string[]` | Yes | — | Input image URL array |
| `outputs` | `number` | No | — | Number to generate |
| `inspiration_id` | `number` | No | — | Inspiration template ID |

---

## 5. TypeScript Interface Definitions

```typescript
// ===================================================
// Common Enums
// ===================================================

/** Current website video IDs; local legacy IDs 29/30 remain accepted separately. */
export type VideoModelType = 1 | 7 | 19 | 21 | 9 | 41 | 3 | 4 | 5 | 6 | 11 | 15 | 27 | 26 | 28 | 91 | 65 | 73 | 71 | 86 | 87 | 92 | 23 | 25 | 63 | 24 | 64 | 89 | 50 | 88 | 151 | 104 | 95 | 168 | 150 | 112 | 166;

/** Image generation model IDs */
export type ImageModelType = 18 | 72 | 37 | 12 | 80 | 165 | 38 | 39 | 40 | 101 | 174 | 175;

/** Video modes supported by this Skill */
export type VideoGenerateType = 0 | 1;

/** Image generation modes */
export type ImageGenerateType =
  | 3   // text-to-image
  | 4;  // image-to-image

// ===================================================
// Video Generation Request Body
// ===================================================

/** Conditional fields depend on model and reference mode; see video-model-catalog.md. */
export interface VideoGeneratePayload {
  model_type: VideoModelType;
  generate_type: VideoGenerateType;
  prompt: string;
  outputs?: number;
  duration?: number;
  resolution?: string;
  ratio?: string;
  is_switch_audio?: 0 | 1;
  image?: string;
  image_tail?: string;
  function_mode?: 0 | 1;
  images?: string[];
  videos?: string[];
  audios?: string[];
  seed?: number;
  cfg_scale?: number;
  motion_mode?: '1' | '2';
  moition_range?: '1' | '2' | '3' | '4';
  style?: string;
  negative_prompt?: string;
  shot_type?: 'single' | 'multi';
  inspiration_id?: string;
}

// ===================================================
// Image Generation Request Body
// ===================================================

/**
 * POST /api/lumeflow/image-generate
 * Full image generation payload
 */
export interface ImageGeneratePayload {
  model_type: ImageModelType;
  generate_type: ImageGenerateType;
  prompt: string;
  ratio?: string;
  resolution?: string;
  outputs?: number;
  images?: string[]; // Required in image mode, model-specific count.
  moition_range?: '2' | '3' | '4'; // GPT quality.
  is_web_search?: 0 | 1; // Seedream Lite selectable.
  inspiration_id?: string;
}

// ===================================================
// Image Effects Request Body
// ===================================================

/**
 * POST /api/lumeflow/image-effects-generate
 * AI image effects payload
 */
export interface ImageEffectsPayload {
  /** Effect ID (from /api/lumeflow/image-effects-special-list) */
  special_id: number;

  /** Input image URL array */
  images: string[];

  /** Number to generate */
  outputs?: number;

  /** Inspiration template ID */
  inspiration_id?: number;
}
```

---

## 6. Parameter Mapping (Frontend → API)

Video generation composable (`useCommonVideoGenerator`) complete mapping:

| Frontend Field (`modelData.xxx`) | API Field (`param.xxx`) |
|----------------------------------|------------------------|
| `prompt` | `prompt` |
| `sound` | `is_switch_audio` |
| `duation` | `duration` (convert to Number) |  <!-- typo in frontend code: should be "duration" -->
| `creativeRelevance` | `cfg_scale` (÷100) |
| `image1` | `image` |
| `image2` | `image_tail` |
| `mode` | `motion_mode` |
| `resolution` | `resolution` |
| `motionRange` | `moition_range` |
| `size` | `ratio` |
| `seed` | `seed` |
| `negative_prompt` | `negative_prompt` |
| `style` | `style` |
| `outputs` | `outputs` (convert to Number) |
| `shot_type` | `shot_type` (1→`'multi'` or `'single'`) |
| `function_mode` | `function_mode` |

---

## 7. Current video business rules

The [current catalog](video-model-catalog.md) and scripts/model_catalog.py are authoritative for the website video model keys, supported modes and parameters. Audio, ratios, duration and resolution depend on model/mode. The price endpoint is authoritative for cost; do not apply generic bulk discounts to every class. Normalize the same request for price and generation. First/end-frame images and reference arrays are distinct modes, and end frames are optional where supported. Upload URLs are required. The current video catalog supersedes all earlier video rules in this analysis.
