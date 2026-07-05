"""Dictionary management commands."""

from __future__ import annotations

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import FluidVoiceError
from fluidvoice_cli.output import emit_json, is_json_mode, log_info, log_success


def run_dict_add_word(
    word: str,
    settings: Settings,
    *,
    definition: str | None = None,
) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            client.add_custom_word(word, definition)
        if is_json_mode():
            emit_json({"word": word, "definition": definition, "status": "added"})
        else:
            log_success(f"Added custom word: {word}")
        return 0
    except FluidVoiceError:
        raise


def run_dict_list_words(settings: Settings, *, limit: int = 100) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            words = client.list_custom_words(limit=limit)
        items = [w.model_dump() for w in words]
        if is_json_mode():
            emit_json({"words": items})
        else:
            for w in words:
                aliases = f" (aliases: {', '.join(w.aliases)})" if w.aliases else ""
                weight = f" [weight={w.weight}]" if w.weight is not None else ""
                detail = f" — {w.definition}" if w.definition else ""
                log_info(f"{w.word}{detail}{aliases}{weight}")
        return 0
    except FluidVoiceError:
        raise


def run_dict_add_replacement(
    original: str,
    replacement: str,
    settings: Settings,
) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            client.add_replacement(original, replacement)
        if is_json_mode():
            emit_json({"original": original, "replacement": replacement, "status": "added"})
        else:
            log_success(f"Added replacement: {original} -> {replacement}")
        return 0
    except FluidVoiceError:
        raise


def run_dict_list_replacements(settings: Settings, *, limit: int = 100) -> int:
    try:
        with FluidVoiceClient(settings) as client:
            rules = client.list_replacements(limit=limit)
        items = [r.model_dump() for r in rules]
        if is_json_mode():
            emit_json({"replacements": items})
        else:
            for r in rules:
                log_info(f"{r.original} -> {r.replacement}")
        return 0
    except FluidVoiceError:
        raise
