"""Terminal and JSON output helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn

_console: Console | None = None
_json_mode = False
_no_color = False
_verbose = False


def init_output(*, json_mode: bool = False, no_color: bool = False, verbose: bool = False) -> None:
    global _console, _json_mode, _no_color, _verbose
    _json_mode = json_mode
    _no_color = no_color or bool(__import__("os").environ.get("NO_COLOR"))
    _verbose = verbose
    _console = Console(stderr=True, no_color=_no_color)


def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console(stderr=True)
    return _console


def is_json_mode() -> bool:
    return _json_mode


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def log_info(message: str) -> None:
    if _json_mode:
        return
    get_console().print(message)


def log_verbose(message: str) -> None:
    if _json_mode or not _verbose:
        return
    get_console().print(f"[dim]{message}[/dim]")


def log_success(message: str) -> None:
    if _json_mode:
        return
    get_console().print(f"[green]{message}[/green]")


def log_transcribe_success(
    *,
    input_path: Path,
    output_path: Path,
    chars: int,
    source: str = "api",
) -> None:
    """Print a clear success summary after transcription."""
    if _json_mode:
        emit_json(
            {
                "status": "success",
                "message": "Transcription complete",
                "input": str(input_path),
                "output": str(output_path),
                "chars": chars,
                "source": source,
            }
        )
        return
    console = get_console()
    console.print("[bold green]✓ Transcription complete[/bold green]")
    console.print(f"  [dim]Input:[/dim]  {input_path.name}")
    console.print(f"  [dim]Output:[/dim] {output_path}")
    console.print(f"  [dim]Size:[/dim]   {chars:,} characters")
    if source == "history_cache":
        console.print("  [dim]Source:[/dim] FluidVoice history cache")


def log_warning(message: str) -> None:
    if _json_mode:
        return
    get_console().print(f"[yellow]{message}[/yellow]")


def log_error(message: str, *, hint: str | None = None) -> None:
    if _json_mode:
        payload: dict[str, Any] = {"error": message}
        if hint:
            payload["hint"] = hint
        emit_json(payload)
        return
    console = get_console()
    console.print(f"[red bold]Error:[/red bold] {message}", style="red")
    if hint:
        for line in hint.split("\n"):
            console.print(f"  [dim]→ {line}[/dim]")


def log_batch_success(*, transcribed: int, skipped: int, failed: int, total: int) -> None:
    """Print a summary after batch transcription."""
    if _json_mode:
        return
    console = get_console()
    console.print()
    console.print("[bold green]✓ Batch complete[/bold green]")
    console.print(f"  [dim]Total:[/dim]       {total} files")
    console.print(f"  [dim]Transcribed:[/dim] {transcribed}")
    if skipped:
        console.print(f"  [dim]Skipped:[/dim]     {skipped} (already exist)")
    if failed:
        console.print(f"  [red]Failed:[/red]       {failed}")
    else:
        console.print("  [dim]Failed:[/dim]       0")


def progress_bar(description: str = "Working") -> Progress:
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=get_console(),
        disable=_json_mode,
    )


def write_stdout(text: str) -> None:
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()
