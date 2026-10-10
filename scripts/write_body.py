#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write JSON body to UTF-8 file (no BOM)
Solves Unicode encoding issues on Windows command line.

Usage:
    # Pass JSON as argument
    python write_body.py --content '{"prompt":"A cat running on grass"}'

    # Pipe JSON via stdin
    echo '{"prompt":"flower"}' | python write_body.py

    # Custom output path
    python write_body.py --content '{"prompt":"test"}' --out-file C:\\tmp\\req.json

Output: prints the file path written to
"""

import json
import os
import sys
import tempfile
import argparse


def main():
    parser = argparse.ArgumentParser(description='Write JSON body to UTF-8 file')
    parser.add_argument('--content', default='', help='JSON body string')
    parser.add_argument('--out-file', default='', help='Output file path')
    args = parser.parse_args()

    # Get JSON from --content param or stdin
    if args.content:
        body = args.content
    elif not sys.stdin.isatty():
        body = sys.stdin.read().strip()
    else:
        body = '{}'

    # Validate JSON
    json.loads(body)

    if args.out_file:
        out_file = args.out_file
        out_dir = os.path.dirname(out_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
    else:
        # Reserve a separate file for every request, including concurrent chats.
        descriptor, out_file = tempfile.mkstemp(prefix='lumeflow_req_', suffix='.json')
        os.close(descriptor)

    # Write with UTF-8 no BOM
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(body)

    print(out_file)


if __name__ == '__main__':
    main()
