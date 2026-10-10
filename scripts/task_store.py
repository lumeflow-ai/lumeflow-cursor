#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task_store.py — Local task registry for Lumeflow generation tasks.

Storage: LUMEFLOW_TASK_STORE_PATH override, or the LumeFlow user data directory.
Existing OpenClaw history is read when the new store does not yet exist.

Schema (lumeflow_tasks.json):
{
  "tasks": [
    {
      "local_id":    "uuid-v4",           # unique local tracking ID
      "task_ids":    [22211],             # remote task ID(s)
      "type":        "video" | "image",
      "status":      "pending" | "processing" | "completed" | "failed",
      "prompt":      "...",
      "model_type":  88,
      "body":        {...},               # full request body snapshot
      "created_at":  "2026-05-19T11:00:00+08:00",
      "updated_at":  "2026-05-19T11:02:30+08:00",
      "result_urls": ["https://..."],
      "integral_used":      50,
      "integral_remaining": 3944,
      "error":       null | "error message"
    }
  ]
}
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from runtime_paths import legacy_paths, readable_path, task_store_path


# ---------------------------------------------------------------------------
# Storage path resolution
# ---------------------------------------------------------------------------

def _task_store_path() -> Path:
    return task_store_path()


TASK_STORE_PATH = _task_store_path()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Current local time as ISO-8601 string with timezone offset."""
    now = datetime.now().astimezone()
    return now.isoformat(timespec='seconds')


def _load() -> dict:
    fallbacks = legacy_paths('tasks') if TASK_STORE_PATH == task_store_path() else []
    path = readable_path(TASK_STORE_PATH, fallbacks)
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass
    return {"tasks": []}


def _save(store: dict) -> None:
    TASK_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASK_STORE_PATH.write_text(
        json.dumps(store, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_task(
    task_ids: list[int],
    task_type: str,
    body: dict,
    integral_used: int = 0,
    integral_remaining: int = 0,
) -> dict:
    """Create and persist a new task record. Returns the task dict."""
    store = _load()
    task = {
        "local_id":           str(uuid.uuid4()),
        "task_ids":           task_ids,
        "type":               task_type,          # "video" | "image"
        "status":             "pending",
        "prompt":             body.get("prompt", ""),
        "model_type":         body.get("model_type"),
        "body":               body,
        "created_at":         _now_iso(),
        "updated_at":         _now_iso(),
        "result_urls":        [],
        "integral_used":      integral_used,
        "integral_remaining": integral_remaining,
        "error":              None,
    }
    store.setdefault("tasks", []).append(task)
    _save(store)
    return task


def update_task(local_id: str, **kwargs) -> Optional[dict]:
    """Update fields of an existing task by local_id. Returns updated task or None."""
    store = _load()
    for task in store.get("tasks", []):
        if task.get("local_id") == local_id:
            kwargs["updated_at"] = _now_iso()
            task.update(kwargs)
            _save(store)
            return task
    return None


def get_task(local_id: str) -> Optional[dict]:
    """Fetch a task by local_id."""
    store = _load()
    for task in store.get("tasks", []):
        if task.get("local_id") == local_id:
            return task
    return None


def list_tasks(status: Optional[str] = None, limit: int = 20) -> list[dict]:
    """List tasks, optionally filtered by status, newest first."""
    store = _load()
    tasks = store.get("tasks", [])
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    # Newest first
    tasks = sorted(tasks, key=lambda t: t.get("created_at", ""), reverse=True)
    return tasks[:limit]


def dump_store_path() -> str:
    return str(TASK_STORE_PATH)
