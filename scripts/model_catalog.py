"""Current website video catalog, verified from Brr45L3F.js and page components.

Network-free rules used for both pricing and generation. No claim of backend
availability: the current website's model IDs/classes define this catalog.
"""

CATALOG_SOURCE = 'https://www.lumeflow.ai/app/_nuxt/Brr45L3F.js'
CATALOG_CHECKED = '2026-09-30'
MODEL_IDS = {
    'kling1.6': 1, 'kling2.0': 7, 'kling2.5': 19,
    'pix6': 21, 'pix5': 9, 'pix4.5': 41, 'hailuo02': 3,
    'veo3.1': 4, 'veo3fast': 5, 'viduQ1': 6, 'sora2': 11,
    'venus': 15, 'sora2Pro': 27, 'viduQ2': 26, 'pix5.5': 28,
    'kling2.6': 91, 'kling3.0': 65, 'seedance2.0': 73,
    'seedance2.0 fast': 71, 'seedance2.0 vip': 86,
    'seedance2.0 vip fast': 87, 'klingo1': 92, 'hailuo2.3': 23,
    'hailuo2.3 fast': 25, 'wan2.5': 63, 'viduQ2 turbo': 24,
    'wan2.6': 64, 'wan2.7': 89, 'seeance1.5pro': 50, 'pixC1': 88,
    'wanHappyHorse1.1': 151, 'wanHappyHorse': 104,
    'grok_imagine1.5': 95, 'seedance2.5': 168,
    'seedance2.0 mini': 150, 'gemini_omni': 112, 'minimaxH3': 166,
}
MODEL_ALIASES = {
    70: 71, 74: 71, 76: 71, 160: 71, 161: 73, 152: 150,
    153: 150, 130: 21, 32: 64, 22: 63,
}
RATIOS_3 = ['16:9', '1:1', '9:16']
RATIOS_5 = RATIOS_3 + ['4:3', '3:4']
RATIOS_AUTO = ['auto', '16:9', '9:16', '4:3', '3:4', '1:1']
RATIOS_WIDE = RATIOS_AUTO + ['21:9']
PIX_RESOLUTIONS = ['360P', '540P', '720P', '1080P']


def profile(name, frontend_class, durations, resolutions, ratios,
            default_duration=5, default_resolution=None, default_ratio='1:1',
            audio='optional', default_audio=1, prompt_limit=2000, modes=(0, 1),
            frame_tail=False, **extra):
    return dict(name=name, frontend_class=frontend_class, durations=durations,
                resolutions=resolutions, ratios=ratios, default_duration=default_duration,
                default_resolution=default_resolution, default_ratio=default_ratio,
                audio=audio, default_audio=default_audio, prompt_limit=prompt_limit,
                modes=list(modes), frame_tail=frame_tail, **extra)


MODEL_PROFILES = {}
for model, name in [(1, 'Kling 1.6'), (7, 'Kling 2.0'), (19, 'Kling 2.5'),
                    (91, 'Kling 2.6'), (92, 'Kling O1')]:
    MODEL_PROFILES[model] = profile(name, 'Ae', [5, 10], None, RATIOS_3,
        audio='optional' if model == 91 else 'on', default_audio=0 if model == 91 else 1,
        frame_tail=model != 91, image_omit_ratio=True,
        image_prompt_limit=2500, motion_mode=model in {1, 7, 19, 91},
        cfg_scale=model != 92, default_motion_mode='1', legacy_resolution=True)
MODEL_PROFILES[65] = profile('Kling 3.0', 'Ae', list(range(3, 16)),
    ['720P', '1080P', '4K'], RATIOS_3, default_resolution='720P',
    default_ratio='16:9', default_audio=0, prompt_limit=2500,
    frame_tail=True, image_omit_ratio=True, cfg_scale=True)

for model, name in [(9, 'LumeFlow 3.0'), (41, 'Pixverse V5 (pix4.5)'),
                    (28, 'Pixverse V5.5'), (21, 'LumeFlow 4.0'), (88, 'Pixverse C1')]:
    durations = list(range(2, 16)) if model in {21, 88} else [5, 8, 10] if model == 28 else [5, 8]
    by_duration = {seconds: list(PIX_RESOLUTIONS) for seconds in durations}
    if model in {9, 41}:
        by_duration[8] = PIX_RESOLUTIONS[:-1]
    if model == 28:
        by_duration[10] = PIX_RESOLUTIONS[:-1]
    MODEL_PROFILES[model] = profile(name, 'Fe', durations, by_duration,
        RATIOS_5 if model in {21, 28, 88} else RATIOS_3,
        default_resolution='720P' if model == 88 else '540P', default_audio=0,
        prompt_limit=5000 if model in {21, 88} else 2000, frame_tail=True,
        image_omit_ratio=True, seed=model in {9, 21, 88},
        motion_mode=True, default_motion_mode='2', style=model == 41)
for model, name in [(3, 'Hailuo 02'), (23, 'Hailuo 2.3'), (25, 'Hailuo 2.3 Fast')]:
    MODEL_PROFILES[model] = profile(name, 'qt', [6, 10],
        {6: ['768P', '1080P'], 10: ['768P']}, None,
        default_duration=6, default_resolution='768P', audio='off')
for model, name in [(4, 'Google Veo 3.1'), (5, 'Google Veo 3.1 Fast')]:
    MODEL_PROFILES[model] = profile(name, 'Zt', [8], None, ['16:9', '9:16'],
        default_duration=8, default_ratio='16:9', audio='on')
MODEL_PROFILES[6] = profile('Vidu Q1', '_t', None, None, RATIOS_3,
    default_duration=None, audio='off', image_omit_ratio=True, vidu_motion=True,
    style=True)
MODEL_PROFILES[26] = profile('Vidu Q2', '_t', [5, 10], ['540P', '720P', '1080P'],
    ['4:3', '3:4'], default_resolution='720P', default_ratio='4:3', audio='off', modes=(0,))
MODEL_PROFILES[24] = profile('Vidu Q2 Turbo', '_t', [5, 10], ['540P', '720P', '1080P'],
    None, default_resolution='540P', audio='off', modes=(1,), vidu_motion=True)
for model, name in [(11, 'Sora 2'), (27, 'Sora 2 Pro')]:
    MODEL_PROFILES[model] = profile(name, 'vt', [10, 15, 25] if model == 27 else [10, 15],
        ['1080P'] if model == 27 else ['720P'], ['16:9', '9:16'],
        default_duration=10, default_resolution='1080P' if model == 27 else '720P',
        default_ratio='9:16', audio='on', image_omit_ratio=model == 11)
MODEL_PROFILES[15] = profile('Venus AI 1.0', 'uo', [5, 10], ['480P', '720P', '1080P'],
    ['21:9', '16:9', '1:1', '3:4', '9:16'], default_resolution='480P',
    default_ratio='9:16', default_audio=0, frame_tail=True)
for model, name in [(63, 'Wan 2.5'), (64, 'Wan 2.6'), (89, 'Wan 2.7')]:
    MODEL_PROFILES[model] = profile(name, 'ot', [5, 10] if model == 63 else list(range(2, 16)),
        ['480P', '720P', '1080P'] if model == 63 else ['720P', '1080P'], RATIOS_5,
        default_resolution='480P' if model == 63 else '720P', default_ratio='16:9', audio='on',
        prompt_limit=5000 if model == 89 else 2000, frame_tail=model == 89,
        image_omit_ratio=True, seed=True, shot_type=model == 64)
for model, name in [(104, 'Happy Horse 1.0'), (151, 'Happy Horse 1.1')]:
    MODEL_PROFILES[model] = profile(name, 'eo', list(range(3, 16)), ['720P', '1080P'],
        RATIOS_5, default_resolution='720P', default_ratio='16:9',
        audio='omit', prompt_limit=5000, seed=True, reference_images=9)
MODEL_PROFILES[50] = profile('Seedance 1.5 Pro', 'ro', list(range(4, 13)),
    ['480P', '720P', '1080P'], RATIOS_WIDE, default_resolution='480P',
    default_ratio='auto', default_audio=0, frame_tail=True)
MODEL_PROFILES[95] = profile('Grok Imagine 1.5', 'lu', [10, 15], ['720P'],
    ['Auto', '2:3', '3:2', '1:1', '9:16', '16:9'], default_duration=10,
    default_resolution='720P', default_ratio='Auto', audio='on', prompt_limit=4000, modes=(1,))
MODEL_PROFILES[112] = profile('Gemini Omni', 'hi', [6, 8, 10], ['720P', '1080P'],
    ['16:9', '9:16'], default_duration=6, default_resolution='720P',
    default_ratio='16:9', audio='on')
for model, name, class_name in [(73, 'Seedance 2.0', 'Xe'), (71, 'Seedance 2.0 Fast', 'Ye'),
    (86, 'Seedance 2.0 VIP', 'ke'), (87, 'Seedance 2.0 VIP Fast', 'Ee'),
    (150, 'Seedance 2.0 Mini', 'je'), (168, 'Seedance 2.5', 'Le'), (166, 'MiniMax H3', 'Me')]:
    MODEL_PROFILES[model] = profile(name, class_name,
        list(range(4, 31 if model == 168 else 16)),
        ['768P', '2K'] if model == 166 else ['480P', '720P'] + (['1080P'] if model in {73, 86} else []),
        RATIOS_WIDE if model in {86, 87, 168, 166} else RATIOS_AUTO,
        default_resolution='768P' if model == 166 else '480P', default_ratio='auto',
        audio='optional' if model in {86, 87, 168} else 'on', prompt_limit=5000,
        frame_tail=True, omni=True,
        reference_limits={'images': 30 if model == 168 else 9,
                          'videos': 1 if model in {71, 73} else 10 if model == 168 else 3,
                          'audios': 0 if model in {71, 73} else 10 if model == 168 else 3},
        frame_auto_ratio=model in {168, 166}, text_auto_ratio=model == 166)

for _key, _id in MODEL_IDS.items():
    MODEL_PROFILES[_id]['key'] = _key


def integer(value, field):
    if isinstance(value, bool):
        raise ValueError(f'{field} must be an integer')
    try:
        number = float(value)
        result = int(number)
        if number != result:
            raise ValueError()
        return result
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f'{field} must be an integer') from None


def resolve_model_type(value):
    if isinstance(value, str):
        name = value.strip().casefold()
        # Also accept readable labels and the corrected spelling of the site's typo.
        names = {key.casefold(): model for key, model in MODEL_IDS.items()}
        names.update({p['name'].casefold(): model for model, p in MODEL_PROFILES.items()})
        names.update({'seedance1.5pro': 50, 'pixverse v4.5': 41, 'pixverse v5': 41,
                      'lumeflow 3.0': 9, 'lumeflow 4.0': 21})
        if name in names:
            return names[name]
    model = integer(value, 'model_type')
    return MODEL_ALIASES.get(model, model)


def urls(body, field, limit):
    values = body.get(field, [])
    if not isinstance(values, list) or any(not isinstance(url, str) or not url.strip() for url in values):
        raise ValueError(f'{field} must be an array of non-empty URLs')
    if len(values) > limit:
        raise ValueError(f'Model {body["model_type"]} accepts at most {limit} {field}')
    return values


def frame_url(body, field, required=False):
    value = body.get(field, '')
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f'{field} must be a non-empty image URL' if required else f'{field} must be a URL string or empty')


def normalize_video_request(body):
    """Normalize a copied API body without accessing credentials or the network."""
    body = dict(body)
    if body.get('model_type') in (None, ''):
        return body
    model = resolve_model_type(body['model_type'])
    body['model_type'] = model
    p = MODEL_PROFILES.get(model)
    if p is None:
        return body  # Preserve legacy/custom API requests outside this website catalog.
    kind = integer(body.get('generate_type', 0), 'generate_type')
    if kind not in p['modes']:
        raise ValueError(f'{p["name"]} supports generate_type values {p["modes"]}')
    body['generate_type'] = kind
    prompt = body.get('prompt')
    prompt_limit = p.get('image_prompt_limit', p['prompt_limit']) if kind == 1 else p['prompt_limit']
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > prompt_limit:
        raise ValueError(f'{p["name"]} prompt must be non-empty text of at most {prompt_limit} characters')
    output_count = integer(body.get('outputs', 1), 'outputs')
    if not 1 <= output_count <= 4:
        raise ValueError('outputs must be between 1 and 4')
    body['outputs'] = output_count
    if p['durations'] is None:
        body.pop('duration', None)  # Vidu Q1 has no duration control in its request class.
    else:
        duration = integer(body.get('duration', p['default_duration']), 'duration')
        if duration not in p['durations']:
            raise ValueError(f'Invalid duration for {p["name"]}; allowed: {p["durations"]}')
        body['duration'] = duration
    resolutions = p['resolutions']
    if p.get('legacy_resolution'):
        body.setdefault('resolution', '720P')  # Ae.toPlain includes this internal default.
    elif resolutions is None:
        body.pop('resolution', None)
    else:
        allowed = resolutions.get(body['duration'], []) if isinstance(resolutions, dict) else resolutions
        value = body.get('resolution', p['default_resolution'])
        resolution = next((r for r in allowed if isinstance(value, str) and r.casefold() == value.strip().casefold()), None)
        if resolution is None:
            raise ValueError(f'Invalid resolution for {p["name"]}; allowed: {allowed}')
        body['resolution'] = resolution
    mode = integer(body.get('function_mode', 0), 'function_mode')
    if mode not in {0, 1} or (mode and (not p.get('omni') or kind != 1)):
        raise ValueError('Omni requires a supported model, generate_type=1 and function_mode=1')
    if p.get('omni') and kind == 1:
        body['function_mode'] = mode
    else:
        body.pop('function_mode', None)
    if mode == 1:
        limits = p['reference_limits']
        materials = sum(len(urls(body, field, limit)) for field, limit in limits.items())
        if materials == 0:
            raise ValueError('Omni requires at least one reference material')
        for field, limit in limits.items():
            if limit == 0:
                body.pop(field, None)
        body.pop('image', None)
        body.pop('image_tail', None)
    elif kind == 1 and p.get('reference_images'):
        # Upgrade the skill's previous single-image Happy Horse requests to the website format.
        if not body.get('images') and body.get('image'):
            frame_url(body, 'image', required=True)
            body['images'] = [body['image']]
        if not urls(body, 'images', p['reference_images']):
            raise ValueError(f'{p["name"]} requires reference images')
        if urls(body, 'videos', 0) or urls(body, 'audios', 0):
            raise ValueError('Happy Horse accepts image references only')
        if body.get('image_tail'):
            raise ValueError('Happy Horse uses images[] instead of image_tail')
        body.pop('image', None)
        body.pop('image_tail', None)
        body.pop('videos', None)
        body.pop('audios', None)
    else:
        if any(urls(body, field, 0) for field in ('images', 'videos', 'audios')):
            raise ValueError('Reference arrays require a supported reference mode')
        for field in ('images', 'videos', 'audios'):
            body.pop(field, None)
        if kind == 0:
            if body.get('image') or body.get('image_tail'):
                raise ValueError('Text-to-video does not accept frame images')
            body.pop('image', None)
            body.pop('image_tail', None)
        else:
            frame_url(body, 'image', required=True)
            frame_url(body, 'image_tail')
            if body.get('image_tail') and not p['frame_tail']:
                raise ValueError(f'{p["name"]} does not expose end-frame control')
            if not p['frame_tail']:
                body.pop('image_tail', None)
    if p['audio'] == 'omit':
        body.pop('is_switch_audio', None)
    else:
        audio = integer(body.get('is_switch_audio', p['default_audio']), 'is_switch_audio')
        if audio not in {0, 1}:
            raise ValueError('is_switch_audio must be 0 or 1')
        body['is_switch_audio'] = 1 if p['audio'] == 'on' else 0 if p['audio'] == 'off' else audio
    ratio_options = p['ratios']
    if ratio_options is None or (kind == 1 and p.get('image_omit_ratio')):
        body.pop('ratio', None)
    else:
        value = body.get('ratio', p['default_ratio'])
        ratio = next((r for r in ratio_options if isinstance(value, str) and r.casefold() == value.casefold()), None)
        if ratio is None:
            raise ValueError(f'Invalid ratio for {p["name"]}; allowed: {ratio_options}')
        if (kind == 1 and mode == 0 and p.get('frame_auto_ratio')) or (kind == 0 and p.get('text_auto_ratio')):
            ratio = 'auto'
        if model == 63 and kind == 0 and body['resolution'] == '480P' and ratio in {'4:3', '3:4'}:
            raise ValueError('Wan 2.5 at 480P accepts only 16:9, 9:16 and 1:1')
        body['ratio'] = ratio
    if p.get('motion_mode'):
        default_mode = '2' if model in {1, 19} and kind == 1 and body.get('image_tail') else p.get('default_motion_mode', '1')
        value = str(body.get('motion_mode', default_mode))
        if value not in {'1', '2'}:
            raise ValueError('motion_mode must be 1 (standard) or 2 (professional)')
        if model in {1, 19} and kind == 1 and body.get('image_tail') and value != '2':
            raise ValueError('Kling 1.6/2.5 end-frame control requires professional motion_mode=2')
        body['motion_mode'] = value
    else:
        body.pop('motion_mode', None)
    if 'cfg_scale' in body:
        if not p.get('cfg_scale'):
            body.pop('cfg_scale')
        elif isinstance(body['cfg_scale'], bool) or not isinstance(body['cfg_scale'], (int, float)) or not 0 <= body['cfg_scale'] <= 1:
            raise ValueError('cfg_scale must be between 0 and 1')
    if not p.get('seed'):
        body.pop('seed', None)
    elif 'seed' in body:
        seed = integer(body['seed'], 'seed')
        if not 0 <= seed <= 2147483647:
            raise ValueError('seed must be between 0 and 2147483647')
        body['seed'] = seed
    if p.get('vidu_motion'):
        value = str(body.get('moition_range', '1'))  # Preserve the API's spelling.
        if value not in {'1', '2', '3', '4'}:
            raise ValueError('moition_range must be 1, 2, 3 or 4')
        body['moition_range'] = value
    else:
        body.pop('moition_range', None)
    if p.get('style') and not (model == 6 and kind == 1):
        value = str(body.get('style', '0'))
        allowed = {'0', '1'} if model == 6 else {'0', '1', '2', '3', '4', '5'}
        if value not in allowed:
            raise ValueError(f'Invalid style; allowed: {sorted(allowed)}')
        body['style'] = value
    else:
        body.pop('style', None)
    if model != 9:
        body.pop('negative_prompt', None)
    if p.get('shot_type'):
        value = body.get('shot_type', 'multi')
        if value in (1, '1', 'multi'):
            body['shot_type'] = 'multi'
        elif value in (0, '0', 'single'):
            body['shot_type'] = 'single'
        else:
            raise ValueError('shot_type must be single or multi')
    else:
        body.pop('shot_type', None)
    return body


def list_models():
    return {'source': CATALOG_SOURCE, 'checked': CATALOG_CHECKED,
            'models': [{'model_type': model, **p} for model, p in MODEL_PROFILES.items()]}
