"""
Firebase Realtime Database utilities.
Shared by all agents and services.
"""

import requests
import json
from datetime import datetime, timezone
from typing import Optional
from .config import FIREBASE_DB_URL

_BASE = FIREBASE_DB_URL


def fb_write(path: str, data) -> dict:
    """PUT data at path."""
    r = requests.put(f"{_BASE}{path}.json", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def fb_push(path: str, data) -> dict:
    """POST (push) data at path — auto-generates key."""
    r = requests.post(f"{_BASE}{path}.json", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def fb_read(path: str) -> Optional[dict]:
    """GET data at path."""
    r = requests.get(f"{_BASE}{path}.json", timeout=10)
    r.raise_for_status()
    return r.json()


def fb_delete(path: str):
    """DELETE data at path."""
    r = requests.delete(f"{_BASE}{path}.json", timeout=10)
    r.raise_for_status()


def fb_patch(path: str, data: dict) -> dict:
    """PATCH (merge) data at path."""
    r = requests.patch(f"{_BASE}{path}.json", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def push_alert(title: str, content: str, severity: str = "info",
               source: str = "backend", alert_type: str = "system"):
    """Push an alert to Fund HQ."""
    import uuid
    alert_id = f"{source}-{uuid.uuid4().hex[:8]}"
    alert = {
        "id": alert_id,
        "type": alert_type,
        "title": title,
        "content": content,
        "severity": severity,
        "dismissed": False,
        "created": datetime.now(timezone.utc).isoformat(),
        "source": source,
    }
    fb_write(f"/fundHQ/alerts/{alert_id}", alert)
    return alert_id


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
