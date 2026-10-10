#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lumeflow Login Script

Implements the OpenClaw login_key flow:
  1. Generate a UUID v4 login_key
  2. Call get-login-url to obtain the browser redirect URL
  3. Notify user to open the browser and complete login
  4. Poll poll-api-key every 5s until api_key is obtained (server times out at ~180s)
  5. Persist api_key privately for all Lumeflow skills (never print it)

Usage:
    # Full login flow (opens browser, polls, saves api_key)
    python login.py

    # Only generate the login URL (no browser, no polling)
    python login.py --action login-url

    # Poll with a known login_key (e.g. if browser was opened manually)
    python login.py --action poll --login-key a1b2c3d4-e5f6-7890-abcd-ef1234567890
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
import tempfile
from pathlib import Path
from runtime_paths import product_config_path
import urllib.request
import urllib.error
import urllib.parse


try:
    from product_config import resolve_runtime_config, _product_config_path
    _CFG = resolve_runtime_config()
    BASE_URL = _CFG.get('LUMEFLOW_BASE_URL') or 'https://lac-api.imyfone.com'
except Exception:
    BASE_URL = 'https://lac-api.imyfone.com'

# Poll config: every 5 seconds, server returns timeout after ~180s
POLL_INTERVAL = 5       # seconds
POLL_TIMEOUT  = 200     # Client safety margin, slightly above server's 180s
LOGIN_URL_PATH = '/api/lumeflow/openclaw/auth/login-url'
API_KEY_PATH   = '/api/lumeflow/openclaw/auth/api-key'


def _get_product_config_path():
    """Use the same writable path as product_config.py, outside the plugin."""
    return str(product_config_path())


def generate_login_key():
    """Generate a UUID v4 login_key."""
    return str(uuid.uuid4())


def get_login_url(login_key):
    """Call the login-url endpoint to get the browser redirect URL."""
    url = f'{BASE_URL}{LOGIN_URL_PATH}?login_key={login_key}'
    req = urllib.request.Request(url, method='GET')

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode('utf-8'))
            if body.get('code') == 200 and body.get('data', {}).get('login_url'):
                return body['data']['login_url']
            return {'error': 'Unexpected response', 'detail': body}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        return {'error': f'HTTP {e.code}', 'detail': error_body}
    except urllib.error.URLError as e:
        return {'error': str(e.reason)}


def poll_api_key(login_key, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
    """Poll the api-key endpoint until the user completes login or server/client timeout.

    Server returns status='timeout' after ~180s if user never logged in.
    Client hard-limit is POLL_TIMEOUT (200s) as a safety net.
    """
    url = f'{BASE_URL}{API_KEY_PATH}?login_key={login_key}'
    deadline = time.time() + timeout
    elapsed  = 0

    while time.time() < deadline:
        req = urllib.request.Request(url, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                data = body.get('data', {})
                status = data.get('status')

                if status == 'ready':
                    return {'status': 'ready', 'api_key': data.get('api_key')}
                elif status == 'timeout':
                    # Server-side timeout: login_key has expired
                    return {'status': 'timeout', 'message': 'Login session expired on server (login_key timed out after 180s)'}
                elif status == 'error':
                    return {'status': 'error', 'message': data.get('message', 'Unknown error')}
                # status == 'pending', keep polling
                elapsed += interval
                print(f'  ⏳ Waiting for login... ({elapsed}s elapsed)', file=sys.stderr)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            # Network hiccup, skip this tick and retry
            print(f'  ⚠️  Network error, retrying: {e}', file=sys.stderr)

        time.sleep(interval)

    return {'status': 'timeout', 'message': f'Client timeout: login not completed within {timeout} seconds'}


def open_browser(url):
    """Open URL in the default browser. Returns True if browser was launched."""
    try:
        if sys.platform == 'win32':
            os.startfile(url)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        else:
            subprocess.Popen(['xdg-open', url])
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def persist_api_key(api_key):
    """Atomically save credentials without changing shell/OS environment settings."""
    if not isinstance(api_key, str) or not api_key.strip():
        raise RuntimeError('Login response did not include a valid API key')
    target = Path(_get_product_config_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    source = _product_config_path()
    existing = {}
    if source.is_file():
        existing = json.loads(source.read_text(encoding='utf-8'))
        if not isinstance(existing, dict):
            raise RuntimeError('Lumeflow product config must be an object')
    existing['LUMEFLOW_API_KEY'] = api_key
    descriptor, temporary = tempfile.mkstemp(prefix='.lumeflow-', suffix='.json', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(existing, handle, ensure_ascii=False, indent=2)
        if os.name != 'nt':
            os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f'Credentials saved to: {target}', file=sys.stderr)


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------

def action_login_url(login_key):
    """Get the login URL only (no browser, no polling)."""
    result = get_login_url(login_key)
    if isinstance(result, dict) and 'error' in result:
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({
        'login_key': login_key,
        'login_url': result,
    }, ensure_ascii=False, indent=2))


def action_poll(login_key, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
    """Poll for api_key with a known login_key, then persist on success."""
    result = poll_api_key(login_key, timeout=timeout, interval=interval)
    if result.get('status') == 'ready':
        api_key = result['api_key']
        persist_api_key(api_key)
        print(json.dumps({
            'status': 'success',
            'authenticated': True,
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            'status': result.get('status', 'error'),
            'message': result.get('message', 'Unknown error'),
        }, ensure_ascii=False))
        sys.exit(1)


def action_login(timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
    """Full login flow: generate key -> notify user -> open browser -> poll -> persist."""
    login_key = generate_login_key()

    # Step 1: Get login URL
    login_url = get_login_url(login_key)
    if isinstance(login_url, dict) and 'error' in login_url:
        print(json.dumps(login_url, ensure_ascii=False))
        sys.exit(1)

    # Step 2: Notify user to log in (regardless of whether browser opens)
    print('', file=sys.stderr)
    print('🔐 Please open the following link to complete Lumeflow login:', file=sys.stderr)
    print(f'   {login_url}', file=sys.stderr)
    print('', file=sys.stderr)
    print(f'⏳ Waiting for login, polling every {interval}s, server timeout ~180s...', file=sys.stderr)
    print('', file=sys.stderr)

    # Step 3: Try to open browser (optional, failure does not affect the flow)
    browser_opened = open_browser(login_url)
    if not browser_opened:
        print('⚠️  Could not open browser automatically. Please copy the link above and open it manually.', file=sys.stderr)
        print('', file=sys.stderr)

    # Step 4: Poll (5s interval, server returns status=timeout after 180s)
    result = poll_api_key(login_key, timeout=timeout, interval=interval)

    if result.get('status') == 'ready':
        api_key = result['api_key']
        persist_api_key(api_key)
        print('', file=sys.stderr)
        print('✅ Login successful! api_key has been persisted. All Lumeflow plugins will use this key automatically.', file=sys.stderr)
        print(json.dumps({
            'status': 'success',
            'authenticated': True,
        }, ensure_ascii=False, indent=2))
    else:
        print('', file=sys.stderr)
        status = result.get('status', 'error')
        message = result.get('message', 'Unknown error')
        if status == 'timeout':
            print('⏰ Login timed out: you did not complete login in time. Please re-run the script to get a new login link.', file=sys.stderr)
        else:
            print(f'❌ Login failed: {message}', file=sys.stderr)
        print(json.dumps({
            'status': status,
            'message': message,
        }, ensure_ascii=False))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Lumeflow login tool')
    parser.add_argument('--action', default='login',
                        choices=['login', 'login-url', 'poll'],
                        help='Action to perform (default: login)')
    parser.add_argument('--login-key', default='',
                        help='Existing login_key for poll action')
    parser.add_argument('--timeout', type=int, default=POLL_TIMEOUT,
                        help=f'Poll timeout in seconds (default: {POLL_TIMEOUT})')
    parser.add_argument('--interval', type=int, default=POLL_INTERVAL,
                        help=f'Poll interval in seconds (default: {POLL_INTERVAL})')
    args = parser.parse_args()

    if args.timeout <= 0 or args.interval <= 0:
        parser.error('--timeout and --interval must be positive')

    if args.action == 'login':
        action_login(timeout=args.timeout, interval=args.interval)

    elif args.action == 'login-url':
        login_key = args.login_key or generate_login_key()
        action_login_url(login_key)

    elif args.action == 'poll':
        if not args.login_key:
            print(json.dumps({'error': '--login-key is required for poll action'}, ensure_ascii=False))
            sys.exit(1)
        action_poll(args.login_key, timeout=args.timeout, interval=args.interval)


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError):
        print(json.dumps({'status': 'error', 'message': 'Login credentials could not be saved. Check the private config path and permissions.'}))
        sys.exit(1)
