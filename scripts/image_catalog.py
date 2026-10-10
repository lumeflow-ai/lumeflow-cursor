"""Image request rules from DVQTaBJ-.js; no network or credential access."""

from model_catalog import integer

IMAGE_SOURCE = 'https://www.lumeflow.ai/app/_nuxt/DVQTaBJ-.js'
IMAGE_CHECKED = '2026-09-30'
IMAGE_IDS = {
    'nanobanana': 18, 'nanobanana2': 72, 'nanobananaPro': 37,
    'seedream4.0': 12, 'seedream5.0': 80, 'seedream5Pro': 165,
    'klingO1': 38, 'fluxKontextMax': 39, 'fluxKontextPro': 40,
    'gptImage2': 101, 'gptImage25': 174,
}
RATIOS = ['1:1', '4:3', '3:4', '16:9', '9:16', '3:2', '2:3']
WIDE = RATIOS + ['21:9']


def profile(key, name, cls, resolutions, prompt_limits, references, ratios=RATIOS,
            default_ratio='1:1', modes=(3, 4), **extra):
    return dict(key=key, name=name, frontend_class=cls, resolutions=resolutions,
                prompt_limits=prompt_limits, reference_images=references,
                ratios=ratios, default_ratio=default_ratio, modes=list(modes), **extra)


IMAGE_PROFILES = {
    18: profile('nanobanana', 'Nano Banana V1', 'Ce', None, [1500, 2000], 5,
                text_ratios=WIDE),
    72: profile('nanobanana2', 'Nano Banana V2', 'Ce', ['1K', '2K', '4K'],
                [5000, 5000], 14, ['auto'] + RATIOS + ['5:4', '4:5'], 'auto'),
    37: profile('nanobananaPro', 'Nano Banana Pro', 'Ce', ['1K', '2K', '4K'],
                [1500, 2000], 5, text_resolutions=['2K', '4K']),
    12: profile('seedream4.0', 'Seedream 4.0', 'Re', ['1K', '2K', '4K'],
                [600, 600], 10, None, '', web_search='fixed'),
    80: profile('seedream5.0', 'Seedream 5.0 Lite', 'Re', ['2K', '3K'],
                [2000, 2000], 14, WIDE, '16:9', web_search='optional'),
    165: profile('seedream5Pro', 'Seedream 5.0 Pro', 'Re', ['1K', '2K'],
                 [2000, 2000], 10, WIDE, '16:9'),
    38: profile('klingO1', 'Kling O1 Image', 'at', ['1K', '2K'],
                [600, 2000], 9, WIDE, modes=[4]),
    39: profile('fluxKontextMax', 'Flux Kontext Max', 'tt', [], [600, 1000], 10),
    40: profile('fluxKontextPro', 'Flux Kontext Pro', 'ot', [], [1000, 1000], 10),
    101: profile('gptImage2', 'GPT Image 2', '_e', ['1K', '2K', '4K'],
                 [5000, 5000], 3, WIDE + ['9:21'], '16:9', quality=True, upload_mib=5),
    174: profile('gptImage25', 'GPT Image 2.5 Flare', 'je', ['1K', '2K', '4K'],
                 [5000, 5000], 16, ['auto'] + RATIOS, 'auto', quality=True, upload_mib=5),
    175: profile('gptImage25Sunburst', 'GPT Image 2.5 Sunburst', 'je', ['1K', '2K', '4K'],
                 [5000, 5000], 16, ['auto'] + RATIOS, 'auto', quality=True, upload_mib=5),
}


def resolve_image_model(value):
    if isinstance(value, str):
        names = {key.casefold(): model for key, model in IMAGE_IDS.items()}
        names.update({p['name'].casefold(): model for model, p in IMAGE_PROFILES.items()})
        names.update({p['key'].casefold(): model for model, p in IMAGE_PROFILES.items()})
        names.update({'nano banana': 18, 'nano banana 2': 72, 'seedream 5.0': 80,
                      'gpt image 2.5': 174, 'gptimage25flare': 174, 'kling o1': 38})
        if value.strip().casefold() in names:
            return names[value.strip().casefold()]
    model = integer(value, 'model_type')
    return 72 if model == 108 else model


def normalize_image_request(body):
    if not isinstance(body, dict):
        raise ValueError('Image request body must be a JSON object')
    body = dict(body)
    model = resolve_image_model(body.get('model_type', 72))
    body['model_type'] = model
    p = IMAGE_PROFILES.get(model)
    if p is None:
        return body  # Keep custom numeric models outside the website catalog working.
    kind = integer(body.get('generate_type', 3), 'generate_type')
    if kind not in p['modes']:
        raise ValueError(f'{p["name"]} supports generate_type values {p["modes"]}')
    body['generate_type'] = kind
    limit = p['prompt_limits'][kind - 3]
    if not isinstance(body.get('prompt'), str) or not body['prompt'].strip() or len(body['prompt']) > limit:
        raise ValueError(f'{p["name"]} prompt must be non-empty text of at most {limit} characters')
    outputs = integer(body.get('outputs', 1), 'outputs')
    if not 1 <= outputs <= 4:
        raise ValueError('outputs must be between 1 and 4')
    body['outputs'] = outputs
    images = body.get('images', [])
    if not isinstance(images, list) or any(not isinstance(url, str) or not url.strip() for url in images):
        raise ValueError('images must be an array of non-empty image URLs')
    if kind == 4:
        if not 1 <= len(images) <= p['reference_images']:
            raise ValueError(f'{p["name"]} requires 1-{p["reference_images"]} reference images')
    else:
        if images:
            raise ValueError('Text-to-image does not accept reference images; use generate_type=4')
        body.pop('images', None)
    if body.get('image') or body.get('image_tail') or body.get('videos') or body.get('audios'):
        raise ValueError('Image generation uses images[] instead of video/frame reference fields')
    ratios = p.get('text_ratios', p['ratios']) if kind == 3 else p['ratios']
    if ratios is None:
        body['ratio'] = ''  # Seedream 4.0 sends empty size; no ratio selector.
    else:
        value = body.get('ratio', p['default_ratio'])
        if value not in ratios:
            raise ValueError(f'Invalid ratio for {p["name"]}; allowed: {ratios}')
        body['ratio'] = value
    resolutions = p.get('text_resolutions', p['resolutions']) if kind == 3 else p['resolutions']
    if resolutions is None:
        body.pop('resolution', None)  # Banana V1 explicitly deletes resolution.
    elif not resolutions:
        body['resolution'] = ''  # Flux toPlain retains empty resolution, no selector.
    else:
        value = body.get('resolution', resolutions[0])
        resolution = next((r for r in resolutions if isinstance(value, str) and value.upper() == r), None)
        if resolution is None:
            raise ValueError(f'Invalid resolution for {p["name"]}; allowed: {resolutions}')
        body['resolution'] = resolution
    if p.get('quality'):
        quality = str(body.get('moition_range', '2'))
        if quality not in {'2', '3', '4'}:
            raise ValueError('moition_range must be 2 (low), 3 (medium) or 4 (high)')
        body['moition_range'] = quality
    else:
        body.pop('moition_range', None)
    if p.get('web_search'):
        value = integer(body.get('is_web_search', 0), 'is_web_search')
        if value not in {0, 1}:
            raise ValueError('is_web_search must be 0 or 1')
        body['is_web_search'] = value if p['web_search'] == 'optional' else 0
    else:
        body.pop('is_web_search', None)
    for field in ('duration', 'is_switch_audio', 'motion_mode', 'function_mode', 'cfg_scale',
                  'style', 'seed', 'negative_prompt', 'shot_type', 'image', 'image_tail',
                  'videos', 'audios', 'size', 'motionRange'):
        body.pop(field, None)
    return body


def list_image_models():
    return {'type': 'image', 'source': IMAGE_SOURCE, 'checked': IMAGE_CHECKED,
            'models': [{'model_type': model, **p} for model, p in IMAGE_PROFILES.items()]}
