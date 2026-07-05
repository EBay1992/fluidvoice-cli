"""FluidVoice CLI entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer

from fluidvoice_cli import __version__
from fluidvoice_cli.commands import (
    batch,
    dictionary,
    doctor,
    health,
    history_cmd,
    postprocess,
    transcribe,
)
from fluidvoice_cli.config import Settings, load_settings
from fluidvoice_cli.errors import FluidVoiceError
from fluidvoice_cli.output import init_output, log_error

app = typer.Typer(
    name="fluidvoice",
    help="Professional CLI for the FluidVoice Local API on macOS.",
    no_args_is_help=True,
    add_completion=True,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"fluidvoice {__version__}")
        raise typer.Exit()


def _resolve_settings(ctx: typer.Context) -> Settings:
    if ctx.obj is None:
        raise typer.Exit(1)
    return ctx.obj


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Machine-readable JSON output."),
    ] = False,
    no_color: Annotated[bool, typer.Option("--no-color", help="Disable colored output.")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose logging.")] = False,
    host: Annotated[str | None, typer.Option("--host", envvar="FLUIDVOICE_HOST")] = None,
    port: Annotated[int | None, typer.Option("--port", envvar="FLUIDVOICE_PORT")] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Config TOML path."),
    ] = None,
    chunk_seconds: Annotated[
        int | None,
        typer.Option("--chunk-seconds", envvar="FLUIDVOICE_CHUNK_SECONDS"),
    ] = None,
    max_direct_seconds: Annotated[
        float | None,
        typer.Option("--max-direct-seconds", envvar="FLUIDVOICE_MAX_DIRECT_SECONDS"),
    ] = None,
) -> None:
    """FluidVoice companion CLI."""
    init_output(json_mode=json_output, no_color=no_color, verbose=verbose)
    base = load_settings(config)
    ctx.obj = base.with_overrides(
        host=host,
        port=port,
        chunk_seconds=chunk_seconds,
        max_direct_seconds=max_direct_seconds,
    )


@app.command("health")
def health_cmd(ctx: typer.Context) -> None:
    """Check FluidVoice Local API health."""
    health.run_health(_resolve_settings(ctx))


@app.command("doctor")
def doctor_cmd(ctx: typer.Context) -> None:
    """Run preflight checks (platform, ffmpeg, Local API)."""
    doctor.run_doctor(_resolve_settings(ctx))


@app.command("transcribe")
def transcribe_cmd(
    ctx: typer.Context,
    file: Annotated[Path, typer.Argument(help="Media file to transcribe.")],
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="Custom output path (default: same name .txt beside file).",
        ),
    ] = None,
    stdout: Annotated[
        bool,
        typer.Option("--stdout", help="Print transcript to terminal instead of saving a file."),
    ] = False,
    no_chunking: Annotated[bool, typer.Option("--no-chunking")] = False,
) -> None:
    """Transcribe a single audio or video file."""
    transcribe.run_transcribe(
        file,
        _resolve_settings(ctx),
        output=output,
        use_chunking=not no_chunking,
        to_stdout=stdout,
    )


@app.command("batch")
def batch_cmd(
    ctx: typer.Context,
    directory: Annotated[Path, typer.Argument(help="Directory with media files.")],
    pattern: Annotated[list[str] | None, typer.Option("--pattern")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir")] = None,
    skip_existing: Annotated[bool, typer.Option("--skip-existing/--no-skip-existing")] = True,
    use_history_cache: Annotated[bool, typer.Option("--use-history-cache")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Batch-transcribe media files in a directory."""
    patterns = tuple(pattern) if pattern else batch.DEFAULT_PATTERNS
    batch.run_batch(
        directory,
        _resolve_settings(ctx),
        patterns=patterns,
        output_dir=output_dir,
        skip_existing=skip_existing,
        use_history_cache=use_history_cache,
        dry_run=dry_run,
    )


history_app = typer.Typer(help="Transcription history commands.")
app.add_typer(history_app, name="history")


@history_app.command("list")
def history_list_cmd(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit")] = 50,
    offset: Annotated[int, typer.Option("--offset")] = 0,
    plist: Annotated[bool, typer.Option("--plist", help="Read plist cache only.")] = False,
) -> None:
    """List transcription history entries."""
    history_cmd.run_history_list(
        _resolve_settings(ctx),
        limit=limit,
        offset=offset,
        use_plist=plist,
    )


@history_app.command("export")
def history_export_cmd(
    ctx: typer.Context,
    output_dir: Annotated[Path, typer.Argument()],
    limit: Annotated[int, typer.Option("--limit")] = 500,
) -> None:
    """Export history transcripts to text files."""
    history_cmd.run_history_export(_resolve_settings(ctx), output_dir, limit=limit)


@app.command("postprocess")
def postprocess_cmd(
    ctx: typer.Context,
    text: Annotated[str, typer.Argument(help="Text to enhance.")],
    mode: Annotated[Literal["dictate", "edit"], typer.Option("--mode")] = "dictate",
    context: Annotated[str | None, typer.Option("--context")] = None,
) -> None:
    """AI-enhance text via FluidVoice postprocess API."""
    postprocess.run_postprocess(text, _resolve_settings(ctx), mode=mode, context=context)


dict_app = typer.Typer(help="Dictionary management.")
app.add_typer(dict_app, name="dict")


@dict_app.command("add-word")
def dict_add_word_cmd(
    ctx: typer.Context,
    word: Annotated[str, typer.Argument()],
    definition: Annotated[str | None, typer.Option("--definition")] = None,
) -> None:
    """Add a custom dictionary word."""
    dictionary.run_dict_add_word(word, _resolve_settings(ctx), definition=definition)


@dict_app.command("list-words")
def dict_list_words_cmd(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit")] = 100,
) -> None:
    """List custom dictionary words."""
    dictionary.run_dict_list_words(_resolve_settings(ctx), limit=limit)


@dict_app.command("add-replacement")
def dict_add_replacement_cmd(
    ctx: typer.Context,
    original: Annotated[str, typer.Argument()],
    replacement: Annotated[str, typer.Argument()],
) -> None:
    """Add a dictionary replacement rule."""
    dictionary.run_dict_add_replacement(original, replacement, _resolve_settings(ctx))


@dict_app.command("list-replacements")
def dict_list_replacements_cmd(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit")] = 100,
) -> None:
    """List dictionary replacement rules."""
    dictionary.run_dict_list_replacements(_resolve_settings(ctx), limit=limit)


config_app = typer.Typer(help="Configuration commands.")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show_cmd(ctx: typer.Context) -> None:
    """Show resolved configuration."""
    from fluidvoice_cli.output import emit_json, is_json_mode, log_info

    settings = _resolve_settings(ctx)
    data = settings.model_dump()
    data["base_url"] = settings.base_url
    if is_json_mode():
        emit_json(data)
    else:
        for key, value in data.items():
            log_info(f"{key}: {value}")


def run() -> None:
    try:
        app()
    except FluidVoiceError as exc:
        log_error(exc.message, hint=exc.hint)
        raise typer.Exit(exc.exit_code) from exc


if __name__ == "__main__":
    run()
