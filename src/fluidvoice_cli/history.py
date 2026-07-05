"""History cache: API primary, plist fallback."""

from __future__ import annotations

import json
import os
import plistlib
import re
import subprocess
import tempfile

from fluidvoice_cli.client import FluidVoiceClient, HistoryEntry


def history_from_api(client: FluidVoiceClient, *, limit: int = 500) -> dict[str, str]:
    """Build filename -> text map from /v1/history."""
    texts: dict[str, str] = {}
    entries = client.history(limit=limit, offset=0)
    by_name: dict[str, HistoryEntry] = {}
    for entry in entries:
        name = entry.fileName
        if not name:
            continue
        prev = by_name.get(name)
        if prev is None or (entry.timestamp or "") > (prev.timestamp or ""):
            by_name[name] = entry

    for name, entry in by_name.items():
        text = entry.text.strip()
        if not text:
            continue
        texts[name] = text
        m = re.match(r"^(\d{3})\b", name)
        if m:
            texts[m.group(1)] = text
    return texts


def history_from_plist() -> dict[str, str]:
    """Read FluidVoice plist history (fallback when API history is empty)."""
    try:
        raw = subprocess.check_output(["defaults", "export", "com.FluidApp.app", "-"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}

    with tempfile.NamedTemporaryFile(suffix=".plist", delete=False) as f:
        f.write(raw)
        plist_path = f.name

    try:
        with open(plist_path, "rb") as f:
            data = plistlib.load(f)
    finally:
        os.unlink(plist_path)

    entries = data.get("FileTranscriptionHistoryEntries")
    if not entries:
        return {}
    if isinstance(entries, bytes):
        entries = json.loads(entries.decode("utf-8"))

    by_name: dict[str, dict] = {}
    for entry in entries:
        name = entry.get("fileName")
        if not name:
            continue
        if name not in by_name or entry.get("timestamp", 0) > by_name[name].get("timestamp", 0):
            by_name[name] = entry

    texts: dict[str, str] = {}
    for name, entry in by_name.items():
        text = str(entry.get("text", "")).strip()
        if not text:
            continue
        texts[name] = text
        m = re.match(r"^(\d{3})\b", name)
        if m:
            texts[m.group(1)] = text
    return texts


def load_history_cache(client: FluidVoiceClient, *, limit: int = 500) -> dict[str, str]:
    """Merge API history with plist fallback."""
    texts = history_from_api(client, limit=limit)
    if not texts:
        texts = history_from_plist()
    else:
        texts = {**history_from_plist(), **texts}
    return texts


def lookup_cached_text(cache: dict[str, str], filename: str) -> str | None:
    if filename in cache:
        return cache[filename]
    prefix = filename[:3]
    if prefix in cache:
        return cache[prefix]
    return None
