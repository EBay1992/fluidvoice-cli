"""Terminal and JSON output helpers."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn

_console: Console | None = None
_json_mode = False
_no_color = False


def init_output(*, json_mode: bool = False, no_color: bool = False, verbose: bool = False) -> None:
    global _console, _json_mode, _no_color
    _json_mode = json_mode
    _no_color = no_color or bool(__import__("os").environ.get("NO_COLOR"))
    _console = Console(stderr=True, no_color=_no_color, quiet=not verbose)


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
    get_console().print(f"[dim]{message}[/dim]")


def log_success(message: str) -> None:
    if _json_mode:
        return
    get_console().print(f"[green]{message}[/green]")


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
