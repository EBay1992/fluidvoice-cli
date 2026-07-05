"""Batch transcribe command."""

from __future__ import annotations

from pathlib import Path

import typer

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import EXIT_PARTIAL_BATCH_FAILURE, EXIT_SUCCESS, FluidVoiceError
from fluidvoice_cli.history import load_history_cache, lookup_cached_text
from fluidvoice_cli.media import probe_duration, transcribe_with_chunking
from fluidvoice_cli.output import (
    emit_json,
    is_json_mode,
    log_batch_success,
    log_error,
    log_info,
    log_transcribe_success,
    log_verbose,
    progress_bar,
)

DEFAULT_PATTERNS = ("*.mp4", "*.wav", "*.m4a", "*.ogg", "*.mp3", "*.mov", "*.mkv")


def collect_files(directory: Path, patterns: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    return sorted(set(files))


def run_batch(
    directory: Path,
    settings: Settings,
    *,
    patterns: tuple[str, ...] = DEFAULT_PATTERNS,
    output_dir: Path | None = None,
    skip_existing: bool = True,
    use_history_cache: bool = False,
    dry_run: bool = False,
) -> int:
    if not directory.is_dir():
        raise typer.BadParameter(f"Directory not found: {directory}")

    files = collect_files(directory, patterns)
    if not files:
        log_info(f"No files matching {patterns} in {directory}")
        return EXIT_SUCCESS

    if dry_run:
        payload = {"dry_run": True, "files": [str(f) for f in files]}
        if is_json_mode():
            emit_json(payload)
        else:
            for f in files:
                log_info(f"would transcribe: {f.name}")
        return EXIT_SUCCESS

    history_cache: dict[str, str] = {}
    failed = 0
    transcribed = 0
    skipped = 0
    results: list[dict[str, object]] = []

    with FluidVoiceClient(settings) as client:
        if use_history_cache:
            history_cache = load_history_cache(client, limit=settings.history_limit)
            if history_cache and not is_json_mode():
                log_verbose(f"Loaded {len(history_cache)} history cache entries")

        progress = progress_bar("Batch transcribe")
        with progress:
            task = progress.add_task("batch", total=len(files))
            for idx, media_file in enumerate(files, 1):
                out_base = output_dir or media_file.parent
                txt_path = out_base / f"{media_file.stem}.txt"

                min_bytes = settings.skip_existing_min_bytes
                if skip_existing and txt_path.exists() and txt_path.stat().st_size > min_bytes:
                    if not is_json_mode():
                        log_verbose(f"[{idx}/{len(files)}] skip existing: {media_file.name}")
                    results.append(
                        {
                            "file": str(media_file),
                            "status": "skipped",
                            "output": str(txt_path),
                        }
                    )
                    skipped += 1
                    progress.advance(task)
                    continue

                if not is_json_mode():
                    progress.console.print(f"[{idx}/{len(files)}] {media_file.name}")

                try:
                    if use_history_cache:
                        cached = lookup_cached_text(history_cache, media_file.name)
                    else:
                        cached = None
                    if cached:
                        text = cached
                        source = "history_cache"
                        if not is_json_mode():
                            log_verbose("  using history cache")
                    else:

                        def do_transcribe(path: Path) -> str:
                            return client.transcribe(path)

                        duration = probe_duration(media_file)
                        mode = "chunked" if duration > settings.max_direct_seconds else "direct"
                        if not is_json_mode():
                            log_verbose(f"  {mode} transcribe ({duration:.0f}s)")

                        def on_chunk(i: int, total: int) -> None:
                            if not is_json_mode():
                                log_verbose(f"    chunk {i}/{total}")

                        text = transcribe_with_chunking(
                            media_file,
                            do_transcribe,
                            chunk_seconds=settings.chunk_seconds,
                            max_direct_seconds=settings.max_direct_seconds,
                            on_chunk=on_chunk,
                        )
                        source = "api"

                    txt_path.write_text(text + "\n", encoding="utf-8")
                    if not is_json_mode():
                        log_transcribe_success(
                            input_path=media_file,
                            output_path=txt_path,
                            chars=len(text),
                            source=source,
                        )
                    results.append(
                        {
                            "file": str(media_file),
                            "status": "ok",
                            "output": str(txt_path),
                            "chars": len(text),
                            "source": source,
                        }
                    )
                    transcribed += 1
                except FluidVoiceError as exc:
                    failed += 1
                    if not is_json_mode():
                        log_error(exc.message, hint=exc.hint)
                    results.append(
                        {
                            "file": str(media_file),
                            "status": "error",
                            "error": exc.message,
                        }
                    )
                progress.advance(task)

    if is_json_mode():
        emit_json(
            {
                "status": "success" if failed == 0 else "partial",
                "message": "Batch complete",
                "total": len(files),
                "transcribed": transcribed,
                "skipped": skipped,
                "failed": failed,
                "results": results,
            }
        )
    else:
        log_batch_success(
            transcribed=transcribed,
            skipped=skipped,
            failed=failed,
            total=len(files),
        )

    if failed:
        raise typer.Exit(EXIT_PARTIAL_BATCH_FAILURE)
    return EXIT_SUCCESS
