"""Doctor / preflight checks."""

from __future__ import annotations

import platform
import shutil

import typer

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import EXIT_FLUID_NOT_RUNNING, EXIT_SUCCESS, FluidVoiceError
from fluidvoice_cli.output import (
    emit_json,
    is_json_mode,
    log_error,
    log_success,
    log_warning,
)


def run_doctor(settings: Settings) -> int:
    checks: list[dict[str, object]] = []
    ok = True

    system = platform.system()
    checks.append({"name": "platform", "ok": system == "Darwin", "detail": system})
    if system != "Darwin":
        ok = False
        log_warning("FluidVoice runs on macOS only; CLI client logic works elsewhere for testing")

    for tool in ("ffmpeg", "ffprobe"):
        found = shutil.which(tool) is not None
        checks.append({"name": tool, "ok": found, "detail": shutil.which(tool) or "not found"})
        if not found:
            log_warning(f"{tool} not found — required for long media chunking")

    api_ok = False
    api_status = "unreachable"
    try:
        with FluidVoiceClient(settings) as client:
            health = client.health()
            api_ok = True
            api_status = health.status
    except FluidVoiceError as exc:
        api_status = exc.message

    checks.append(
        {
            "name": "local_api",
            "ok": api_ok,
            "detail": api_status,
            "url": settings.base_url,
        }
    )
    if not api_ok:
        ok = False

    if is_json_mode():
        emit_json({"ok": ok, "checks": checks})
    else:
        for check in checks:
            name = str(check["name"])
            if check["ok"]:
                log_success(f"{name}: {check['detail']}")
            else:
                log_error(f"{name}: {check['detail']}")
        if ok:
            log_success("All checks passed")
        else:
            log_error("Some checks failed")

    if not api_ok:
        raise typer.Exit(EXIT_FLUID_NOT_RUNNING)
    return EXIT_SUCCESS if ok else EXIT_FLUID_NOT_RUNNING
