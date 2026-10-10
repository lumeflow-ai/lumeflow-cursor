#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lumeflow API sign generator (Python)

Usage:
    # Method 1: Read body from file (recommended for Chinese content)
    python sign.py --body-file /tmp/lumeflow_req.json

    # Method 2: Pass JSON as argument
    python sign.py --body '{"prompt":"flower","generate_type":0}'

    # Method 3: Pipe JSON via stdin
    echo '{"prompt":"flower"}' | python sign.py

    # Method 4: GET requests with extra query params
    python sign.py --extra-params "ids=123"

    # Combine body file + extra params
    python sign.py --body-file /tmp/lumeflow_req.json --extra-params "ids=123"

Output: timestamp=1234567890&sign=ABCDEF1234567890ABCDEF1234567890
"""

import hashlib
import json
import sys
import time
import argparse

SIGN_KEY = '351f4b0d34e21efede761c88b74b9783feb6aae4'


def generate_sign(body_json='{}', extra_params=''):
    timestamp = str(int(time.time()))
    param = {}

    # Parse body JSON and add non-object/non-array values
    body = json.loads(body_json)
    for key, val in body.items():
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


def main():
    parser = argparse.ArgumentParser(description='Lumeflow API sign generator')
    parser.add_argument('--body', default='', help='JSON body string')
    parser.add_argument('--body-file', default='', help='Path to JSON body file (UTF-8)')
    parser.add_argument('--extra-params', default='', help='Extra query params (e.g. ids=123)')
    args = parser.parse_args()

    # Determine JSON body source: file > argument > stdin > empty
    if args.body_file:
        with open(args.body_file, 'r', encoding='utf-8') as f:
            body_json = f.read().strip()
    elif args.body:
        body_json = args.body
    elif not sys.stdin.isatty():
        body_json = sys.stdin.read().strip()
        if not body_json:
            body_json = '{}'
    else:
        body_json = '{}'

    timestamp, sign = generate_sign(body_json, args.extra_params)
    print(f'timestamp={timestamp}&sign={sign}')


if __name__ == '__main__':
    main()
