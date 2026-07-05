"""Health check command."""

from __future__ import annotations

import typer

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import EXIT_SUCCESS, FluidVoiceError
from fluidvoice_cli.output import emit_json, is_json_mode, log_success


def run_health(settings: Settings) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            result = client.health()
        if is_json_mode():
            emit_json({"status": result.status, "base_url": settings.base_url})
        else:
            log_success(f"FluidVoice Local API is healthy ({result.status}) at {settings.base_url}")
        return EXIT_SUCCESS
    except FluidVoiceError as exc:
        raise typer.Exit(exc.exit_code) from exc
