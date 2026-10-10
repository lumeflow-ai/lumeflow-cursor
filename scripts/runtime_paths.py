"""Writable user data paths, independent of the installed skill/plugin location."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def data_dir() -> Path:
    override = os.environ.get('LUMEFLOW_DATA_DIR', '').strip()
    if override:
        return Path(override).expanduser()
    if sys.platform == 'win32':
        return Path(os.environ.get('APPDATA') or Path.home()) / 'lumeflow'
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'Lumeflow'
    return Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share') / 'lumeflow'


def product_config_path() -> Path:
    override = os.environ.get('LUMEFLOW_PRODUCT_CONFIG_PATH', '').strip()
    return Path(override).expanduser() if override else data_dir() / 'products' / 'lumeflow.json'


def task_store_path() -> Path:
    override = os.environ.get('LUMEFLOW_TASK_STORE_PATH', '').strip()
    return Path(override).expanduser() if override else data_dir() / 'lumeflow_tasks.json'


def log_path() -> Path:
    override = os.environ.get('LUMEFLOW_LOG_PATH', '').strip()
    return Path(override).expanduser() if override else data_dir() / 'logs' / 'lumeflow_http.log'


def legacy_paths(kind: str) -> list[Path]:
    """Read old OpenClaw data only when no explicit storage location was selected."""
    override_key = 'LUMEFLOW_PRODUCT_CONFIG_PATH' if kind == 'config' else 'LUMEFLOW_TASK_STORE_PATH'
    if os.environ.get(override_key, '').strip() or os.environ.get('LUMEFLOW_DATA_DIR', '').strip():
        return []
    filename = Path('products/lumeflow.json') if kind == 'config' else Path('lumeflow_tasks.json')
    if sys.platform == 'win32':
        return [Path(os.environ.get('APPDATA') or Path.home()) / 'openclaw' / filename]
    return [Path('/app/data/private') / filename, Path.home() / '.openclaw' / filename]


def readable_path(primary: Path, fallbacks: list[Path]) -> Path:
    if primary.is_file():
        return primary
    return next((path for path in fallbacks if path.is_file()), primary)
