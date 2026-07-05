"""History list and export commands."""

from __future__ import annotations

from pathlib import Path

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import FluidVoiceError
from fluidvoice_cli.history import history_from_plist, load_history_cache
from fluidvoice_cli.output import emit_json, is_json_mode, log_info, log_success


def run_history_list(
    settings: Settings,
    *,
    limit: int = 50,
    offset: int = 0,
    use_plist: bool = False,
) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            if use_plist:
                cache = history_from_plist()
                items = [{"fileName": k, "text": v} for k, v in cache.items()]
            else:
                entries = client.history(limit=limit, offset=offset)
                items = [e.model_dump() for e in entries]

        if is_json_mode():
            emit_json({"items": items, "count": len(items)})
        else:
            for item in items:
                name = item.get("fileName") or item.get("windowTitle") or "unknown"
                text = str(
                    item.get("text")
                    or item.get("finalText")
                    or item.get("processedText")
                    or ""
                )[:80]
                log_info(f"{name}: {text}...")
        return 0
    except FluidVoiceError:
        raise


def run_history_export(
    settings: Settings,
    output_dir: Path,
    *,
    limit: int = 500,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        with FluidVoiceClient(settings) as client:
            cache = load_history_cache(client, limit=limit)

        count = 0
        seen: set[str] = set()
        for name, text in cache.items():
            if len(name) == 3 and name.isdigit():
                continue
            safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in name)
            out = output_dir / f"{safe}.txt"
            if safe in seen:
                continue
            seen.add(safe)
            out.write_text(text + "\n", encoding="utf-8")
            count += 1

        if is_json_mode():
            emit_json({"exported": count, "output_dir": str(output_dir)})
        else:
            log_success(f"Exported {count} transcripts to {output_dir}")
        return 0
    except FluidVoiceError:
        raise
