"""History cache tests."""

from __future__ import annotations

from fluidvoice_cli.history import lookup_cached_text


def test_lookup_by_filename() -> None:
    cache = {"lesson.mp4": "transcript text"}
    assert lookup_cached_text(cache, "lesson.mp4") == "transcript text"


def test_lookup_by_prefix() -> None:
    cache = {"001": "first lesson"}
    assert lookup_cached_text(cache, "001 intro.mp4") == "first lesson"


def test_lookup_miss() -> None:
    assert lookup_cached_text({}, "missing.mp4") is None
