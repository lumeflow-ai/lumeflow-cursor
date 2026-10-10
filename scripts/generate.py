#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lumeflow API all-in-one script (Python)
Handles: write body file + sign generation + HTTP request + query results

No curl needed. No temp file encoding issues. Unicode handled natively by Python.

Usage:
    # Query video generation price before confirmation
    python generate.py --action video-price --body '{"generate_type":0,"model_type":28,"prompt":"A cat running on grass","is_switch_audio":1,"ratio":"1:1","duration":5,"resolution":"540P","motion_mode":"2","outputs":1}'

    # Query image generation price before confirmation
    python generate.py --action image-price --body '{"generate_type":3,"model_type":12,"prompt":"A flower swaying in the wind","ratio":"auto","resolution":"1K","outputs":1}'

    # Generate video (auto query balance before/after)
    python generate.py --action video --body '{"generate_type":0,"model_type":28,"prompt":"A cat running on grass","is_switch_audio":1,"ratio":"1:1","duration":5,"resolution":"540P","motion_mode":"2","outputs":1}'

    # Generate image (auto query balance before/after)
    python generate.py --action image --body '{"generate_type":3,"model_type":12,"prompt":"A flower swaying in the wind","ratio":"auto","resolution":"1K","outputs":1}'

    # Query video task result
    python generate.py --action video-query --ids 456328

    # Query image task result
    python generate.py --action image-query --ids 22211

    # Upload local image
    python generate.py --action upload-image --file C:\\path\\to\\image.png

    # Check balance
    python generate.py --action balance
"""

import hashlib
import json
import logging
import os
import sys
import time
import uuid
import argparse
from datetime import datetime
import urllib.parse
import urllib.request
import urllib.error

from product_config import resolve_runtime_config
from runtime_paths import log_path
from model_catalog import (MODEL_PROFILES, MODEL_IDS, MODEL_ALIASES,
                           normalize_video_request, resolve_model_type, list_models)
from image_catalog import (IMAGE_PROFILES, normalize_image_request,
                           resolve_image_model, list_image_models)

RUNTIME_CONFIG = resolve_runtime_config()
BASE_URL = RUNTIME_CONFIG.get('LUMEFLOW_BASE_URL')
API_KEY = RUNTIME_CONFIG.get('LUMEFLOW_API_KEY')
PLATFORM = os.environ.get('LUMEFLOW_PLATFORM', 'openclaw')
# OPERATING_SYSTEM = os.environ.get('LUMEFLOW_OPERATING_SYSTEM', 'android')
# OPERATING_TYPE = os.environ.get('LUMEFLOW_OPERATING_TYPE', 'app')
VERSION = os.environ.get('LUMEFLOW_VERSION', '1.0.0')
SIGN_KEY = '351f4b0d34e21efede761c88b74b9783feb6aae4'
SUPPORTED_IMAGE_EXTENSIONS = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
}
MAX_UPLOAD_IMAGE_BYTES = 10 * 1024 * 1024
SUPPORTED_AUDIO_EXTENSIONS = {
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.m4a': 'audio/mp4',
    '.aac': 'audio/aac',
    '.ogg': 'audio/ogg',
    '.flac': 'audio/flac',
    '.wma': 'audio/x-ms-wma',
}
MAX_UPLOAD_AUDIO_BYTES = 50 * 1024 * 1024
SUPPORTED_VIDEO_EXTENSIONS = {
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.webm': 'video/webm',
    '.mkv': 'video/x-matroska',
}
MAX_UPLOAD_VIDEO_BYTES = 200 * 1024 * 1024
SKILL_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = str(log_path())
SENSITIVE_HEADER_KEYS = {'api-key'}
SENSITIVE_QUERY_KEYS = {'sign'}
VIDEO_DURATION_RULES = {
    model: {'model_name': p['name'], 'type': 'values', 'values': p['durations']}
    for model, p in MODEL_PROFILES.items() if p['durations'] is not None
}
# Keep numeric legacy IDs accepted without inventing a website remapping.
VIDEO_DURATION_RULES.update({
    29: {'model_name': 'Kling 2.6 (legacy ID)', 'type': 'values', 'values': [5, 10]},
    30: {'model_name': 'Kling O1 (legacy ID)', 'type': 'values', 'values': [5, 10]},
})
UNDOCUMENTED_VIDEO_DURATION_MODELS = {}
VIDEO_RESOLUTION_BY_DURATION = {
    model: p['resolutions'] if isinstance(p['resolutions'], dict) else
        {seconds: p['resolutions'] for seconds in p['durations']}
    for model, p in MODEL_PROFILES.items()
    if p['resolutions'] is not None and p['durations'] is not None
}


def build_logger():
    """Create the file logger used for all HTTP request traces."""
    logger = logging.getLogger('lumeflow_http')
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    os.makedirs(os.path.dirname(os.path.abspath(LOG_FILE_PATH)), exist_ok=True)
    handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    return logger


LOGGER = logging.getLogger('lumeflow_http')


def mask_sensitive_value(value):
    """Mask secrets before writing them to the log file."""
    if value is None:
        return None

    text = str(value)
    if len(text) <= 8:
        return '*' * len(text)
    return f'{text[:4]}***{text[-4:]}'


def sanitize_headers(headers):
    """Hide sensitive headers while keeping the rest readable."""
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADER_KEYS:
            sanitized[key] = mask_sensitive_value(value)
        else:
            sanitized[key] = value
    return sanitized


def sanitize_url(url):
    """Mask sensitive query parameters before logging the URL."""
    parsed = urllib.parse.urlsplit(url)
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    sanitized_pairs = []
    for key, value in query_pairs:
        if key.lower() in SENSITIVE_QUERY_KEYS:
            value = mask_sensitive_value(value)
        sanitized_pairs.append((key, value))
    sanitized_query = urllib.parse.urlencode(sanitized_pairs, safe='*')
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, sanitized_query, parsed.fragment))


def build_request_log_body(body=None, raw_body=None, content_type=''):
    """Prepare a safe request body preview for logging."""
    if body is not None:
        return body

    if raw_body is None:
        return None

    return {
        'content_type': content_type or 'application/octet-stream',
        'byte_length': len(raw_body),
    }


def log_http_event(level, event_type, payload):
    """Write a structured HTTP log line."""
    build_logger().log(level, '%s %s', event_type, json.dumps(payload, ensure_ascii=False))


def current_timestamp():
    """Return a local timestamp with millisecond precision for logs."""
    return datetime.now().astimezone().isoformat(timespec='milliseconds')


def ensure_runtime_config():
    """Fail fast when required runtime configuration is missing."""
    missing = []
    if not API_KEY:
        missing.append('LUMEFLOW_API_KEY')

    if missing:
        from product_config import _product_config_path
        missing_text = ', '.join(missing)
        raise RuntimeError(
            f'Missing required Lumeflow runtime configuration: {missing_text}. '
            f'Expected {_product_config_path()} or env fallback.'
        )


def generate_sign(body_dict=None, extra_params=''):
    """Generate timestamp and sign from body dict and/or extra params."""
    timestamp = str(int(time.time()))
    param = {}

    # Add non-object/non-array values from body
    if body_dict:
        for key, val in body_dict.items():
            if isinstance(val, (list, dict)):
                continue
            param[key] = val

    # Parse extra query params
    if extra_params:
        for pair in extra_params.split('&'):
            if '=' in pair:
                idx = pair.index('=')
                param[pair[:idx]] = pair[idx + 1:]

    # Add timestamp
    param['timestamp'] = timestamp

    # Sort keys and build signing string
    parts = []
    for key in sorted(param.keys()):
        value = param[key]
        if isinstance(value, bool):
            value = '1' if value else ''
        else:
            value = str(value)
        parts.append(f'{key}={value}')

    sign_str = '&'.join(parts) + f'&key={SIGN_KEY}'

    # MD5 hash, uppercase
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    return timestamp, sign


def resolve_media_path(file_path):
    """Resolve media:// URIs to local filesystem paths.

    OpenClaw platform uses media:// protocol for uploaded files.
    Try common storage locations to find the actual file.
    """
    if not file_path.startswith('media://'):
        return file_path

    # Extract filename from URI: media://inbound/xxx.jpg -> xxx.jpg
    filename = file_path.split('/')[-1]
    if not filename:
        return file_path

    search_dirs = [
        os.path.join(os.path.expanduser('~'), '.openclaw', 'media', 'inbound'),
        os.path.join(os.path.expanduser('~'), '.openclaw', 'media'),
        os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace'),
        os.getcwd(),
    ]

    for directory in search_dirs:
        candidate = os.path.join(directory, filename)
        if os.path.isfile(candidate):
            print(f'Resolved media:// path: {file_path} -> {candidate}', file=sys.stderr)
            return candidate

    # Also try a broader search in ~/.openclaw for the filename
    openclaw_root = os.path.join(os.path.expanduser('~'), '.openclaw')
    if os.path.isdir(openclaw_root):
        for root, _dirs, files in os.walk(openclaw_root):
            if filename in files:
                return os.path.join(root, filename)

    return file_path  # return original if not found (will fail validation)


def validate_upload_image(file_path, model=None, function_mode=0, model_kind='video'):
    """Validate upload image path, type and size."""
    if not file_path:
        raise ValueError('No --file provided for image upload')

    file_path = resolve_media_path(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    resolver = resolve_image_model if model_kind == 'image' else resolve_model_type
    catalog = IMAGE_PROFILES if model_kind == 'image' else MODEL_PROFILES
    target = resolver(model) if model not in (None, '') else None
    if target is not None and target not in catalog:
        raise ValueError('Image upload model is not in the website catalog')
    extensions = dict(SUPPORTED_IMAGE_EXTENSIONS)
    max_bytes = MAX_UPLOAD_IMAGE_BYTES
    if model_kind == 'image' and target is not None:
        max_bytes = IMAGE_PROFILES[target].get('upload_mib', 10) * 1024 * 1024
    elif target == 166 or (target == 168 and function_mode == 1):
        max_bytes = 30 * 1024 * 1024
    if model_kind == 'video' and target == 166:
        extensions.update({'.heic': 'image/heic', '.heif': 'image/heif'})
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in extensions:
        supported = ', '.join(ext.lstrip('.') for ext in sorted(extensions))
        raise ValueError(f'Unsupported image format: {ext or "(none)"}. Supported formats: {supported}')

    file_size = os.path.getsize(file_path)
    if file_size > max_bytes:
        raise ValueError(f'File size exceeds {max_bytes // (1024 * 1024)}MiB limit: {file_size} bytes')

    return extensions[ext]


def validate_upload_audio(file_path):
    """Validate upload audio path, type and size."""
    if not file_path:
        raise ValueError('No --file provided for audio upload')

    file_path = resolve_media_path(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        supported = ', '.join(ext.lstrip('.') for ext in sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise ValueError(f'Unsupported audio format: {ext or "(none)"}. Supported formats: {supported}')

    file_size = os.path.getsize(file_path)
    if file_size > MAX_UPLOAD_AUDIO_BYTES:
        raise ValueError(f'File size exceeds 50MB limit: {file_size} bytes')

    return SUPPORTED_AUDIO_EXTENSIONS[ext]


def build_multipart_form_data(file_path, field_name='image', mime_type=None):
    """Build multipart/form-data payload for a single file upload."""
    if mime_type is None:
        mime_type = validate_upload_image(file_path)

    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    boundary = f'----LumeflowBoundary{uuid.uuid4().hex}'
    filename = os.path.basename(file_path)
    body = b''.join([
        f'--{boundary}\r\n'.encode('utf-8'),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode('utf-8'),
        f'Content-Type: {mime_type}\r\n\r\n'.encode('utf-8'),
        file_bytes,
        b'\r\n',
        f'--{boundary}--\r\n'.encode('utf-8'),
    ])
    return body, f'multipart/form-data; boundary={boundary}'


def build_headers():
    """Build request headers shared by generation and balance requests."""
    ensure_runtime_config()
    return {
        'api-key': API_KEY,
        'platform': PLATFORM,
        # 'operating_system': OPERATING_SYSTEM,
        # 'operating_type': OPERATING_TYPE,
        'version': VERSION,
    }


def normalize_number(value):
    """Convert response numeric fields to int/float when possible."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            number = float(value)
        except ValueError:
            return None
        return int(number) if number.is_integer() else number
    return None


def extract_balance_summary(balance_result):
    """Extract comparable balance fields from a balance API response."""
    data = balance_result.get('data') if isinstance(balance_result, dict) else None
    if not isinstance(data, dict):
        return {
            'integral_total': None,
            'voice_free_times': None,
        }
    return {
        'integral_total': normalize_number(data.get('total')),
        'voice_free_times': normalize_number(data.get('voice_free_times')),
    }


def attach_balance_info(result, balance_before, balance_after):
    """Attach balance snapshots and deltas to a generation result."""
    before_summary = extract_balance_summary(balance_before)
    after_summary = extract_balance_summary(balance_after)

    output = dict(result) if isinstance(result, dict) else {'generation': result}
    output['balance_before'] = balance_before
    output['balance_after'] = balance_after
    output['integral_before'] = before_summary['integral_total']
    output['integral_used'] = None
    output['integral_remaining'] = after_summary['integral_total']
    output['voice_free_times_before'] = before_summary['voice_free_times']
    output['voice_free_times_after'] = after_summary['voice_free_times']
    output['voice_free_times_used'] = None

    if before_summary['integral_total'] is not None and after_summary['integral_total'] is not None:
        output['integral_used'] = before_summary['integral_total'] - after_summary['integral_total']

    if before_summary['voice_free_times'] is not None and after_summary['voice_free_times'] is not None:
        output['voice_free_times_used'] = before_summary['voice_free_times'] - after_summary['voice_free_times']

    return output


def parse_int_field(value, field_name):
    """Parse an integer-like request field."""
    if isinstance(value, bool):
        raise ValueError(f'{field_name} must be an integer, got boolean')
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError(f'{field_name} must be an integer, got {value}')
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f'{field_name} cannot be empty')
        try:
            parsed = float(text)
        except ValueError as exc:
            raise ValueError(f'{field_name} must be an integer, got {value!r}') from exc
        if parsed.is_integer():
            return int(parsed)
    raise ValueError(f'{field_name} must be an integer, got {value!r}')


def format_duration_rule(rule):
    """Format a duration rule for user-facing errors."""
    if rule['type'] == 'values':
        values = ', '.join(str(value) for value in rule['values'])
        return f'{values} seconds'
    return f'{rule["min"]}-{rule["max"]} seconds'


def validate_video_duration(body_dict):
    """Validate video duration against the selected model's allowed values."""
    if not isinstance(body_dict, dict):
        raise ValueError('Video request body must be a JSON object')

    model_type_raw = body_dict.get('model_type')
    if model_type_raw in (None, ''):
        return body_dict

    body_dict = normalize_video_request(body_dict)
    model_type = body_dict['model_type']

    undocumented_model_name = UNDOCUMENTED_VIDEO_DURATION_MODELS.get(model_type)
    if undocumented_model_name:
        raise ValueError(
            f'No local duration rule is documented for {undocumented_model_name}. '
            'Check references/ai_models_analysis.md and update the skill before sending this model.'
        )

    rule = VIDEO_DURATION_RULES.get(model_type)
    if rule is None:
        return body_dict

    duration_raw = body_dict.get('duration')
    if duration_raw in (None, ''):
        raise ValueError(
            f'Missing duration for {rule["model_name"]}. '
            f'Allowed durations: {format_duration_rule(rule)}'
        )

    duration = parse_int_field(duration_raw, 'duration')
    body_dict['duration'] = duration

    if rule['type'] == 'values' and duration not in rule['values']:
        allowed = ', '.join(str(value) for value in rule['values'])
        raise ValueError(
            f'Invalid duration {duration}s for {rule["model_name"]}. '
            f'Allowed durations: {allowed}'
        )

    if rule['type'] == 'range' and not (rule['min'] <= duration <= rule['max']):
        raise ValueError(
            f'Invalid duration {duration}s for {rule["model_name"]}. '
            f'Allowed range: {rule["min"]}-{rule["max"]} seconds'
        )

    return body_dict


def validate_video_resolution(body_dict):
    """Validate resolution against duration for models with explicit local rules."""
    if not isinstance(body_dict, dict):
        raise ValueError('Video request body must be a JSON object')

    model_type_raw = body_dict.get('model_type')
    if model_type_raw in (None, ''):
        return body_dict

    model_type = resolve_model_type(model_type_raw)
    by_duration = VIDEO_RESOLUTION_BY_DURATION.get(model_type)
    if not by_duration:
        return body_dict

    duration_raw = body_dict.get('duration')
    if duration_raw in (None, ''):
        return body_dict

    duration = parse_int_field(duration_raw, 'duration')
    allowed = by_duration.get(duration)
    if allowed is None:
        return body_dict

    rule = VIDEO_DURATION_RULES.get(model_type, {})
    model_label = rule.get('model_name', f'model_type {model_type}')

    resolution_raw = body_dict.get('resolution')
    if resolution_raw in (None, ''):
        allowed_text = ', '.join(allowed)
        raise ValueError(
            f'Missing resolution for {model_label} at {duration}s. '
            f'Allowed resolutions: {allowed_text}'
        )

    resolution = str(resolution_raw).strip()
    canon = {value.upper(): value for value in allowed}
    resolved = canon.get(resolution.upper())
    if resolved is None:
        allowed_text = ', '.join(allowed)
        raise ValueError(
            f'Invalid resolution {resolution!r} for {model_label} at {duration}s. '
            f'Allowed resolutions: {allowed_text}'
        )

    body_dict['resolution'] = resolved
    return body_dict


def http_request(url, method='GET', body=None, raw_body=None, content_type=''):
    """Send HTTP request and return parsed JSON response."""
    ensure_runtime_config()
    headers = build_headers()

    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    elif raw_body is not None:
        if content_type:
            headers['Content-Type'] = content_type
        data = raw_body

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    request_id = uuid.uuid4().hex[:12]
    started_at = current_timestamp()
    started_perf = time.perf_counter()

    log_http_event(logging.INFO, 'HTTP_REQUEST', {
        'request_id': request_id,
        'started_at': started_at,
        'method': method,
        'url': sanitize_url(url),
        'headers': sanitize_headers(headers),
        'body': build_request_log_body(body=body, raw_body=raw_body, content_type=content_type),
    })

    try:
        with urllib.request.urlopen(req) as resp:
            response_text = resp.read().decode('utf-8', errors='replace')
            ended_at = current_timestamp()
            elapsed_ms = round((time.perf_counter() - started_perf) * 1000, 2)

            log_http_event(logging.INFO, 'HTTP_RESPONSE', {
                'request_id': request_id,
                'started_at': started_at,
                'ended_at': ended_at,
                'elapsed_ms': elapsed_ms,
                'status_code': resp.status,
                'headers': dict(resp.headers.items()),
                'body': response_text,
            })

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {'raw': response_text}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        ended_at = current_timestamp()
        elapsed_ms = round((time.perf_counter() - started_perf) * 1000, 2)

        log_http_event(logging.ERROR, 'HTTP_RESPONSE', {
            'request_id': request_id,
            'started_at': started_at,
            'ended_at': ended_at,
            'elapsed_ms': elapsed_ms,
            'status_code': e.code,
            'headers': dict(e.headers.items()) if e.headers else {},
            'body': error_body,
        })

        try:
            detail = json.loads(error_body)
        except json.JSONDecodeError:
            detail = error_body
        return {'error': f'HTTP {e.code}', 'detail': detail}
    except urllib.error.URLError as e:
        ended_at = current_timestamp()
        elapsed_ms = round((time.perf_counter() - started_perf) * 1000, 2)

        log_http_event(logging.ERROR, 'HTTP_RESPONSE', {
            'request_id': request_id,
            'started_at': started_at,
            'ended_at': ended_at,
            'elapsed_ms': elapsed_ms,
            'status_code': None,
            'headers': {},
            'body': {'error': str(e.reason)},
        })

        return {'error': str(e.reason)}


def action_generate(endpoint, body_dict):
    """Send generation request (video or image)."""
    if endpoint == 'video-generate':
        body_dict = validate_video_duration(dict(body_dict))
        body_dict = validate_video_resolution(body_dict)
    elif endpoint == 'image-generate':
        body_dict = normalize_image_request(body_dict)
    timestamp, sign = generate_sign(body_dict)
    url = f'{BASE_URL}/api/lumeflow/{endpoint}?timestamp={timestamp}&sign={sign}'
    return http_request(url, method='POST', body=body_dict)


def action_price(route, body_dict):
    """Query generation price for a video/image task before submission.

    Injects a top-level ``type`` field derived strictly from ``route``
    (image-generate -> 'image', video-generate -> 'video') so downstream
    consumers never need to infer the generation type from body/action/memory.
    """
    if route == '/api/lumeflow/video-generate':
        body_dict = validate_video_duration(dict(body_dict))
        body_dict = validate_video_resolution(body_dict)
    elif route == '/api/lumeflow/image-generate':
        body_dict = normalize_image_request(body_dict)
    price_body = dict(body_dict)
    price_body['route'] = route
    timestamp, sign = generate_sign(price_body)
    url = f'{BASE_URL}/api/lumeflow/get-generate-price?timestamp={timestamp}&sign={sign}'
    result = http_request(url, method='POST', body=price_body)
    if isinstance(result, dict):
        if route == '/api/lumeflow/image-generate':
            result['type'] = 'image'
        elif route == '/api/lumeflow/video-generate':
            result['type'] = 'video'
    return result


def action_query(endpoint, ids):
    """Query task results."""
    extra_params = f'ids={ids}'
    timestamp, sign = generate_sign(extra_params=extra_params)
    url = f'{BASE_URL}/api/lumeflow/{endpoint}?ids={ids}&timestamp={timestamp}&sign={sign}'
    return http_request(url, method='GET')


def action_watch(task_type: str, body_dict: dict,
                 poll_interval: int = 8, poll_timeout: int = 600,
                 debug: bool = False) -> dict:
    """Submit a generation task, persist it locally, then poll in foreground until complete.

    Default timeout matches the CLI (600s). For tools with a hard execution limit,
    set a shorter timeout explicitly and re-query the existing IDs after timeout.
    Poll diagnostics are opt-in; HTTP details remain in the local HTTP log.

    Args:
        task_type:     'video' | 'image'
        body_dict:     request body dict
        poll_interval: seconds between each poll (default 8s)
        poll_timeout:  max wait seconds before giving up (default 600s)
        debug:        include poll diagnostics and full stored task/raw response

    Returns the final task dict (with result_urls populated on success).
    """
    import task_store  # lazy import; same directory

    endpoint = f'{task_type}-generate'
    query_endpoint = f'{task_type}-task-list'
    if task_type == 'video':
        body_dict = validate_video_resolution(validate_video_duration(dict(body_dict)))
    elif task_type == 'image':
        body_dict = normalize_image_request(body_dict)

    def debug_print(*args, **kwargs):
        if debug:
            print(*args, **kwargs)

    def watch_result(task):
        if debug:
            return task
        # Keep the complete request in the task store, not in the agent context.
        fields = ('local_id', 'task_ids', 'type', 'status', 'result_urls',
                  'result_urls_watermark', 'result_cover_urls', 'integral_used',
                  'integral_remaining', 'error', 'error_code')
        result = {key: task[key] for key in fields if key in task}
        # Preserve recovery data only when a completed task has no extracted URL.
        if task.get('status') == 'completed' and not (
                task.get('result_urls') or task.get('result_urls_watermark')):
            result['raw_query_response'] = task.get('raw_query_response')
        return result

    # 1. Submit generation request (includes balance snapshot)
    debug_print(json.dumps({'status': 'submitting', 'type': task_type}, ensure_ascii=False), file=sys.stderr)
    gen_result = action_generate_with_balance(endpoint, body_dict)

    if gen_result.get('error') or gen_result.get('code', 200) != 200:
        print(json.dumps({'error': 'Generation request failed', 'detail': gen_result},
                         ensure_ascii=False))
        sys.exit(1)

    raw_ids = gen_result.get('data', [])
    task_ids = raw_ids if isinstance(raw_ids, list) else [raw_ids]
    integral_used      = gen_result.get('integral_used', 0)
    integral_remaining = gen_result.get('integral_remaining', 0)

    # 2. Persist to local task store
    task = task_store.create_task(
        task_ids=task_ids,
        task_type=task_type,
        body=body_dict,
        integral_used=integral_used,
        integral_remaining=integral_remaining,
    )
    local_id = task['local_id']

    debug_print(json.dumps({
        'status':      'submitted',
        'type':        task_type,
        'local_id':    local_id,
        'task_ids':    task_ids,
        'integral_used':      integral_used,
        'integral_remaining': integral_remaining,
        'store_path':  task_store.dump_store_path(),
    }, ensure_ascii=False, indent=2), file=sys.stderr)
    debug_print(f'  ⏳ Polling every {poll_interval}s (max {poll_timeout}s)...', file=sys.stderr)

    # 3. Poll until complete or timeout
    ids_str = ','.join(str(i) for i in task_ids)
    deadline = time.time() + poll_timeout
    elapsed  = 0
    last_raw_query = None  # track the most recent raw API response

    # Status values — the API returns INTEGER status codes in data[*].status
    # 0 = pending/processing, 1 = completed, 2 = cancelled, 3/4 = error
    # Some endpoints also use string values — support both
    PENDING_STATUSES = {
        'pending', 'processing', 'generating', 'queued', 'queue',
        'waiting', 'created', 'running', 'in_progress', 'init',
        '0',           # string form of integer 0
    }
    PENDING_INT = {0}  # integer form

    DONE_STATUSES = {
        'finish', 'finished', 'success', 'succeeded', 'completed',
        'done', 'ok', 'ready',
        '1',           # string form of integer 1
    }
    DONE_INT = {1}     # integer form

    FAIL_STATUSES = {
        'fail', 'failed', 'error', 'cancelled', 'canceled', 'timeout',
        '2', '3', '4',
    }
    FAIL_INT = {2, 3, 4}  # integer form
    # All URL-like fields to scan (image and video)
    URL_FIELDS = (
        'video_url', 'image_url', 'result_url', 'url', 'output_url',
        'file_url', 'download_url', 'cover_url', 'src', 'uri',
        'video', 'image', 'result',
    )

    while time.time() < deadline:
        time.sleep(poll_interval)
        elapsed += poll_interval

        query_result = action_query(query_endpoint, ids_str)
        last_raw_query = query_result  # save for fallback

        # Raw poll responses are emitted only in debug mode.
        debug_print(f'  [poll {elapsed}s] raw response: '
              + json.dumps(query_result, ensure_ascii=False),
              file=sys.stderr)

        if not isinstance(query_result, dict):
            debug_print(f'  ⚠️  Unexpected response type: {type(query_result)}, retrying...',
                  file=sys.stderr)
            continue

        items = query_result.get('data', [])

        # Handle case where data is a dict instead of list (single task)
        if isinstance(items, dict):
            items = [items]
        elif not isinstance(items, list):
            debug_print(f'  ⚠️  data field is not a list: {type(items)}, retrying...', file=sys.stderr)
            continue

        if not items:
            debug_print(f'  ⚠️  Empty data list, retrying...', file=sys.stderr)
            continue

        # Deduplicate items by task ID to avoid duplicate output
        seen_ids = set()
        deduped_items = []
        for _item in items:
            if isinstance(_item, dict):
                _tid = _item.get('id') or _item.get('task_id')
                if _tid is not None and _tid in seen_ids:
                    debug_print(f'  ⏭️  Skipping duplicate item id={_tid}', file=sys.stderr)
                    continue
                if _tid is not None:
                    seen_ids.add(_tid)
            deduped_items.append(_item)
        items = deduped_items

        result_urls = []           # no-watermark video/image URL (field: digital_video / image)
        result_urls_watermark = [] # watermarked video/image URL (field: video / digital_image)
        result_cover_urls = []    # video cover image (single, field: cover_url / cover)
        any_failed  = False
        failed_error_code = None
        failed_error_reason = ''
        all_done    = True  # assume done; set False if any item is still pending

        for item in items:
            if not isinstance(item, dict):
                continue

            # Extract status — try common field names; accept int or str
            raw_status_val = None
            for key in ('status', 'state', 'task_status'):
                if key in item and item[key] is not None:
                    raw_status_val = item[key]
                    break

            if raw_status_val is None:
                raw_status_val = ''

            is_int_status = isinstance(raw_status_val, int)
            raw_status = str(raw_status_val).lower().strip()

            debug_print(f'  [item status] id={item.get("id", "?")} status={raw_status_val!r} (int={is_int_status})',
                  file=sys.stderr)

            # Determine done/fail/pending using both int sets and string sets
            item_failed  = (is_int_status and raw_status_val in FAIL_INT)    or raw_status in FAIL_STATUSES
            item_done    = (is_int_status and raw_status_val in DONE_INT)     or raw_status in DONE_STATUSES
            item_pending = (is_int_status and raw_status_val in PENDING_INT)  or raw_status in PENDING_STATUSES

            if item_failed:
                any_failed = True
                # Capture error_code and reason from failed item
                _ec = item.get('error_code') or item.get('errorCode') or item.get('code')
                _reason = item.get('reason') or item.get('error') or item.get('message') or ''
                if _ec:
                    failed_error_code = _ec
                    failed_error_reason = _reason
            elif item_done or (not item_pending and raw_status == ''):

                def _is_result_url(val):
                    """Accept both HTTP(S) URLs and data URIs (base64 images)."""
                    return isinstance(val, str) and (val.startswith('http') or val.startswith('data:'))

                def _append_unique(lst, val):
                    """Append only if not already present (dedup)."""
                    if _is_result_url(val) and val not in lst:
                        lst.append(val)

                def _extract_from_dict(d, prefix=''):
                    """Recursively extract result URLs from nested dicts (output, taskResultSummary, etc.)."""
                    urls_no_wm = []
                    urls_wm = []
                    covers = []
                    if not isinstance(d, dict):
                        return urls_no_wm, urls_wm, covers
                    # --- Video fields ---
                    # digital_video = no-watermark, video = watermark
                    v = d.get('digital_video')
                    if _is_result_url(v):
                        urls_no_wm.append(v)
                    v = d.get('video')
                    if _is_result_url(v):
                        urls_wm.append(v)
                    # --- Image fields ---
                    # All image result URLs go to no-watermark list
                    for field in ('origin_thumbnail', 'image', 'thumbnail', 'digital_image', 'watermark', 'image_url', 'url', 'result_url', 'src'):
                        v = d.get(field)
                        if _is_result_url(v):
                            urls_no_wm.append(v)
                    # Cover image fields (video tasks)
                    for field in ('cover_url', 'cover', 'cover_image', 'thumbnail_url'):
                        v = d.get(field)
                        if _is_result_url(v):
                            covers.append(v)
                    # Recurse into nested dicts (e.g. output, taskResultSummary, results)
                    for key in ('output', 'taskResultSummary', 'results', 'result', 'data'):
                        child = d.get(key)
                        if isinstance(child, dict):
                            c_no_wm, c_wm, c_covers = _extract_from_dict(child, prefix=key)
                            urls_no_wm.extend(c_no_wm)
                            urls_wm.extend(c_wm)
                            covers.extend(c_covers)
                        elif isinstance(child, list):
                            for elem in child:
                                if isinstance(elem, dict):
                                    c_no_wm, c_wm, c_covers = _extract_from_dict(elem)
                                    urls_no_wm.extend(c_no_wm)
                                    urls_wm.extend(c_wm)
                                    covers.extend(c_covers)
                                elif _is_result_url(elem):
                                    urls_no_wm.append(elem)
                    # Handle images[] array
                    images_list = d.get('images') or []
                    if isinstance(images_list, list):
                        for img in images_list:
                            if isinstance(img, dict):
                                # All image result URLs go to no-watermark list
                                for field in ('origin_thumbnail', 'image', 'thumbnail', 'image_url', 'url', 'digital_image', 'watermark'):
                                    v = img.get(field)
                                    if _is_result_url(v):
                                        urls_no_wm.append(v)
                    return urls_no_wm, urls_wm, covers

                # --- Primary extraction: top-level video fields ---
                _append_unique(result_urls, item.get('digital_video'))
                _append_unique(result_urls_watermark, item.get('video'))

                # --- Primary extraction: top-level image fields (all go to result_urls) ---
                for field in ('origin_thumbnail', 'image', 'thumbnail', 'image_url', 'url'):
                    _append_unique(result_urls, item.get(field))

                # --- Cover image (video tasks) ---
                for cover_field in ('cover_url', 'cover', 'cover_image', 'thumbnail_url'):
                    cv = item.get(cover_field)
                    if _is_result_url(cv):
                        _append_unique(result_cover_urls, cv)
                        break

                # --- Images[] array at top level ---
                images_list = item.get('images') or []
                if isinstance(images_list, list):
                    for img in images_list:
                        if isinstance(img, dict):
                            # All image result URLs go to result_urls
                            for field in ('origin_thumbnail', 'image', 'thumbnail', 'image_url', 'url', 'digital_image', 'watermark'):
                                _append_unique(result_urls, img.get(field))

                # --- Deep extraction from nested structures (output, taskResultSummary, etc.) ---
                nested_no_wm, nested_wm, nested_covers = _extract_from_dict(item)
                for u in nested_no_wm:
                    _append_unique(result_urls, u)
                for u in nested_wm:
                    _append_unique(result_urls_watermark, u)
                for u in nested_covers:
                    _append_unique(result_cover_urls, u)

                # --- Fallback: top-level URL fields from URL_FIELDS ---
                if not result_urls:
                    for field in URL_FIELDS:
                        val = item.get(field)
                        if _is_result_url(val):
                            _append_unique(result_urls, val)
                            break

            elif item_pending:
                all_done = False  # still waiting
            else:
                # Unknown status — be conservative, keep polling
                all_done = False
                debug_print(f'  ⚠️  Unknown status {raw_status_val!r}, keep polling', file=sys.stderr)

        # Summarise this round
        debug_print(f'  → all_done={all_done} any_failed={any_failed} urls={result_urls}',
              file=sys.stderr)

        if any_failed and not result_urls:
            error_msg = f'error_code={failed_error_code}' if failed_error_code else 'One or more tasks failed on server'
            if failed_error_reason:
                error_msg += f' reason={failed_error_reason}'
            task_store.update_task(local_id, status='failed', error=error_msg,
                                   error_code=failed_error_code)
            final = task_store.get_task(local_id)
            final['type'] = task_type
            final['error_code'] = failed_error_code
            final['raw_query_response'] = last_raw_query
            return watch_result(final)

        if all_done and not any_failed:
            task_store.update_task(local_id, status='completed', result_urls=result_urls,
                                   result_urls_watermark=result_urls_watermark,
                                   result_cover_urls=result_cover_urls)
            final = task_store.get_task(local_id)
            final['type'] = task_type
            final['raw_query_response'] = last_raw_query  # Agent can parse this if result_urls is empty
            debug_print(f'  ✅ Completed! {len(result_urls)} result(s) found.', file=sys.stderr)
            return watch_result(final)

    # Client-side timeout
    task_store.update_task(local_id, status='processing',
                           error=f'Client timeout after {poll_timeout}s — task may still be running on server')
    final = task_store.get_task(local_id)
    final['type'] = task_type
    final['raw_query_response'] = last_raw_query  # last poll response — Agent can extract URL from here
    return watch_result(final)



def action_balance():
    """Check account balance."""
    timestamp, sign = generate_sign()
    url = f'{BASE_URL}/api/lumeflow/integral?timestamp={timestamp}&sign={sign}'
    return http_request(url, method='GET')


def action_generate_with_balance(endpoint, body_dict):
    """Query balance before/after generation and attach the delta to the response.

    Injects a top-level ``type`` field derived strictly from ``endpoint``
    (image-generate -> 'image', video-generate -> 'video') so downstream
    consumers never need to infer the generation type from body/action/memory.
    """
    if endpoint == 'video-generate':
        body_dict = validate_video_resolution(validate_video_duration(dict(body_dict)))
    elif endpoint == 'image-generate':
        body_dict = normalize_image_request(body_dict)
    balance_before = action_balance()
    generation_result = action_generate(endpoint, body_dict)
    balance_after = action_balance()
    output = attach_balance_info(generation_result, balance_before, balance_after)
    if endpoint == 'image-generate':
        output['type'] = 'image'
    elif endpoint == 'video-generate':
        output['type'] = 'video'
    return output


def action_upload_image(file_path, model=None, function_mode=0, model_kind='video'):
    """Upload a local image file and return the remote URL."""
    timestamp, sign = generate_sign()
    url = f'{BASE_URL}/api/lumeflow/claw-upload-image?timestamp={timestamp}&sign={sign}'
    file_path = resolve_media_path(file_path)
    mime_type = validate_upload_image(file_path, model=model, function_mode=function_mode,
                                     model_kind=model_kind)
    body, content_type = build_multipart_form_data(file_path, mime_type=mime_type)
    return http_request(url, method='POST', raw_body=body, content_type=content_type)


def validate_upload_video(file_path):
    """Validate upload video path, type and size."""
    if not file_path:
        raise ValueError('No --file provided for video upload')

    file_path = resolve_media_path(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_VIDEO_EXTENSIONS:
        supported = ', '.join(ext.lstrip('.') for ext in sorted(SUPPORTED_VIDEO_EXTENSIONS))
        raise ValueError(f'Unsupported video format: {ext or "(none)"}. Supported formats: {supported}')

    file_size = os.path.getsize(file_path)
    if file_size > MAX_UPLOAD_VIDEO_BYTES:
        raise ValueError(f'File size exceeds 200MB limit: {file_size} bytes')

    return SUPPORTED_VIDEO_EXTENSIONS[ext]


def action_upload_audio(file_path):
    """Upload a local audio file and return the remote URL."""
    mime_type = validate_upload_audio(file_path)
    timestamp, sign = generate_sign()
    url = f'{BASE_URL}/api/lumeflow/claw-upload-image?timestamp={timestamp}&sign={sign}'
    body, content_type = build_multipart_form_data(file_path, mime_type=mime_type)
    return http_request(url, method='POST', raw_body=body, content_type=content_type)


def action_upload_video(file_path):
    """Upload a local video file and return the remote URL."""
    mime_type = validate_upload_video(file_path)
    timestamp, sign = generate_sign()
    url = f'{BASE_URL}/api/lumeflow/claw-upload-image?timestamp={timestamp}&sign={sign}'
    body, content_type = build_multipart_form_data(file_path, mime_type=mime_type)
    return http_request(url, method='POST', raw_body=body, content_type=content_type)


def main():
    parser = argparse.ArgumentParser(description='Lumeflow API all-in-one tool')
    parser.add_argument('--action', required=True,
                        choices=[
                            'video-price', 'image-price',
                            'video', 'image',
                            'watch-video', 'watch-image',   # submit + continuous poll
                            'video-query', 'image-query',
                            'tasks',                        # list local task history
                            'models',                       # local website model catalog
                            'image-models',                 # local image model catalog
                            'upload-image', 'upload-video', 'upload-audio', 'balance',
                        ],
                        help='Action to perform')
    parser.add_argument('--model', default='', help='Model name/ID filter for models or image upload context')
    parser.add_argument('--model-kind', choices=['video', 'image'], default='video',
                        help='Model catalog for image upload context (default: video)')
    parser.add_argument('--function-mode', type=int, choices=[0, 1], default=0,
                        help='Reference mode for model-aware image upload (0=frames, 1=Omni)')
    parser.add_argument('--body', default='', help='JSON body string')
    parser.add_argument('--body-file', default='', help='Path to JSON body file (UTF-8)')
    parser.add_argument('--ids', default='', help='Task IDs for query (comma-separated)')
    parser.add_argument('--file', default='', help='Local file path for image upload')
    parser.add_argument('--wait', type=int, default=0, help='Wait N seconds before executing (e.g. --wait 30)')
    parser.add_argument('--poll-interval', type=int, default=8,
                        help='Seconds between polls for watch actions (default: 8)')
    parser.add_argument('--poll-timeout', type=int, default=600,
                        help='Max seconds to wait in watch mode (default: 600)')
    parser.add_argument('--debug', action='store_true',
                        help='Include watch poll diagnostics and full task/raw response')
    parser.add_argument('--status', default='',
                        help='Filter tasks by status for --action tasks')
    parser.add_argument('--limit', type=int, default=20,
                        help='Max tasks to list for --action tasks (default: 20)')
    args = parser.parse_args()

    # Wait if requested
    if args.wait > 0:
        print(f'Waiting {args.wait} seconds...')
        time.sleep(args.wait)

    # Parse body from: file > argument > stdin
    body_dict = None
    if args.body_file:
        with open(args.body_file, 'r', encoding='utf-8') as f:
            body_dict = json.loads(f.read().strip())
    elif args.body:
        body_dict = json.loads(args.body)
    elif args.action in ('video-price', 'image-price', 'video', 'image') and not sys.stdin.isatty():
        stdin_text = sys.stdin.read().strip()
        if stdin_text:
            body_dict = json.loads(stdin_text)

    result = None
    try:
        if args.action in ('models', 'image-models'):
            is_image = args.action == 'image-models'
            result = list_image_models() if is_image else list_models()
            if args.model:
                selected = resolve_image_model(args.model) if is_image else resolve_model_type(args.model)
                result['models'] = [p for p in result['models'] if p['model_type'] == selected]
                if not result['models']:
                    raise ValueError('Model is not in the current website catalog')

        elif args.action == 'video-price':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for video price query'}, ensure_ascii=False))
                sys.exit(1)
            result = action_price('/api/lumeflow/video-generate', body_dict)

        elif args.action == 'image-price':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for image price query'}, ensure_ascii=False))
                sys.exit(1)
            result = action_price('/api/lumeflow/image-generate', body_dict)

        elif args.action == 'video':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for video generation'}, ensure_ascii=False))
                sys.exit(1)
            result = action_generate_with_balance('video-generate', body_dict)

        elif args.action == 'image':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for image generation'}, ensure_ascii=False))
                sys.exit(1)
            result = action_generate_with_balance('image-generate', body_dict)

        elif args.action == 'watch-video':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for watch-video'}, ensure_ascii=False))
                sys.exit(1)
            result = action_watch('video', body_dict,
                                  poll_interval=args.poll_interval,
                                  poll_timeout=args.poll_timeout, debug=args.debug)

        elif args.action == 'watch-image':
            if not body_dict:
                print(json.dumps({'error': 'No body provided for watch-image'}, ensure_ascii=False))
                sys.exit(1)
            result = action_watch('image', body_dict,
                                  poll_interval=args.poll_interval,
                                  poll_timeout=args.poll_timeout, debug=args.debug)

        elif args.action == 'video-query':
            if not args.ids:
                print(json.dumps({'error': 'No --ids provided'}, ensure_ascii=False))
                sys.exit(1)
            result = action_query('video-task-list', args.ids)

        elif args.action == 'image-query':
            if not args.ids:
                print(json.dumps({'error': 'No --ids provided'}, ensure_ascii=False))
                sys.exit(1)
            result = action_query('image-task-list', args.ids)

        elif args.action == 'tasks':
            import task_store
            tasks = task_store.list_tasks(
                status=args.status or None,
                limit=args.limit
            )
            result = {
                'tasks': tasks,
                'count': len(tasks),
                'store_path': task_store.dump_store_path(),
            }

        elif args.action == 'upload-image':
            result = action_upload_image(args.file, model=args.model, function_mode=args.function_mode,
                                         model_kind=args.model_kind)

        elif args.action == 'upload-video':
            result = action_upload_video(args.file)

        elif args.action == 'upload-audio':
            result = action_upload_audio(args.file)

        elif args.action == 'balance':
            result = action_balance()
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        sys.exit(1)

    if result is None:
        print(json.dumps({'error': f'Unhandled action: {args.action}'}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
