"""Postprocess command."""

from __future__ import annotations

from typing import Literal

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import FluidVoiceError
from fluidvoice_cli.output import emit_json, is_json_mode, write_stdout


def run_postprocess(
    text: str,
    settings: Settings,
    *,
    mode: Literal["dictate", "edit"] = "dictate",
    context: str | None = None,
) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            result = client.postprocess(text, mode=mode, context=context)
        if is_json_mode():
            emit_json({"text": result, "mode": mode})
        else:
            write_stdout(result)
        return 0
    except FluidVoiceError:
        raise
