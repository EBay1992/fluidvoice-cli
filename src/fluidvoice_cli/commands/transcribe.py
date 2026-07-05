"""Single-file transcribe command."""

from __future__ import annotations

from pathlib import Path

import typer

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import FluidVoiceError
from fluidvoice_cli.media import probe_duration, transcribe_with_chunking
from fluidvoice_cli.output import is_json_mode, log_info, log_transcribe_success, write_stdout


def default_output_path(source: Path) -> Path:
    """Same folder as source, same stem, .txt extension."""
    return source.with_suffix(".txt")


def run_transcribe(
    file: Path,
    settings: Settings,
    *,
    output: Path | None = None,
    use_chunking: bool = True,
    to_stdout: bool = False,
) -> int:
    if not file.is_file():
        raise typer.BadParameter(f"File not found: {file}")

    file = file.resolve()
    out_path = output if output is not None else default_output_path(file)

    try:
        with FluidVoiceClient(settings) as client:

            def do_transcribe(path: Path) -> str:
                return client.transcribe(path)

            if use_chunking:
                duration = probe_duration(file)
                mode = "chunked" if duration > settings.max_direct_seconds else "direct"
                if not is_json_mode():
                    log_info(f"Transcribing {file.name} ({duration:.0f}s, {mode})")

                def on_chunk(i: int, total: int) -> None:
                    if not is_json_mode():
                        log_info(f"  chunk {i}/{total}")

                text = transcribe_with_chunking(
                    file,
                    do_transcribe,
                    chunk_seconds=settings.chunk_seconds,
                    max_direct_seconds=settings.max_direct_seconds,
                    on_chunk=on_chunk,
                )
            else:
                text = do_transcribe(file)

        if to_stdout:
            if is_json_mode():
                from fluidvoice_cli.output import emit_json

                emit_json({"file": str(file), "text": text, "status": "success"})
            else:
                write_stdout(text)
        else:
            out_path.write_text(text + "\n", encoding="utf-8")
            log_transcribe_success(
                input_path=file,
                output_path=out_path,
                chars=len(text),
            )
        return 0
    except FluidVoiceError as exc:
        raise typer.Exit(exc.exit_code) from exc
