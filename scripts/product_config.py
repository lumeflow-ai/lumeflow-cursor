#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from runtime_paths import legacy_paths, product_config_path, readable_path

DEFAULT_BASE_URL = "https://lac-api.imyfone.com"
_CONFIG_KEYS = (
    "LUMEFLOW_BASE_URL",
    "LUMEFLOW_API_KEY",
)
_COMPATIBILITY_ENV_KEYS = {
    "LUMEFLOW_BASE_URL": ("BASE_URL",),
    "LUMEFLOW_API_KEY": ("API_KEY",),
}


def _default_product_config_path() -> Path:
    """Return the writable config path shared with login.py."""
    return product_config_path()


def _product_config_path() -> Path:
    return readable_path(_default_product_config_path(), legacy_paths('config'))


def _load_file_config(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid Lumeflow product config JSON: {path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"Lumeflow product config must be an object: {path}")

    config: dict[str, str] = {}
    for key in _CONFIG_KEYS:
        value = payload.get(key)
        if value is None:
            continue
        normalized_value = str(value).strip()
        if normalized_value:
            config[key] = normalized_value
    return config


def _read_skill_base_url() -> str | None:
    """Read base URL from <skill_dir>/baseurlconfig file (plain text, one line)."""
    # This file is in <skill_dir>/scripts/product_config.py
    # baseurlconfig is at <skill_dir>/baseurlconfig
    skill_dir = Path(__file__).resolve().parent.parent
    config_file = skill_dir / "baseurlconfig"
    if config_file.is_file():
        try:
            url = config_file.read_text(encoding="utf-8").strip()
            if url:
                return url
        except OSError:
            pass
    return None


def resolve_runtime_config() -> dict[str, str]:
    file_config = _load_file_config(_product_config_path())
    resolved: dict[str, str] = {}

    # Priority for LUMEFLOW_BASE_URL:
    #   1. <skill_dir>/baseurlconfig file
    #   2. product config file / env var (standard resolution)
    #   3. DEFAULT_BASE_URL
    skill_base_url = _read_skill_base_url()

    for key in _CONFIG_KEYS:
        # Special handling for BASE_URL
        if key == "LUMEFLOW_BASE_URL" and skill_base_url:
            resolved[key] = skill_base_url
            continue

        if key in file_config:
            resolved[key] = file_config[key]
            continue

        for env_key in (key, *_COMPATIBILITY_ENV_KEYS.get(key, ())):
            value = os.environ.get(env_key, "").strip()
            if value:
                resolved[key] = value
                break

    # Default BASE_URL if not resolved
    if "LUMEFLOW_BASE_URL" not in resolved:
        resolved["LUMEFLOW_BASE_URL"] = DEFAULT_BASE_URL

    return resolved
