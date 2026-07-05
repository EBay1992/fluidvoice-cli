"""Client tests with mocked HTTP."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from fluidvoice_cli.client import FluidVoiceClient
from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import APIError, FluidNotRunningError, TranscribeError


@pytest.fixture
def settings() -> Settings:
    return Settings(host="127.0.0.1", port=47733)


@respx.mock
def test_health_ok(settings: Settings) -> None:
    respx.get("http://127.0.0.1:47733/v1/health").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    with FluidVoiceClient(settings) as client:
        result = client.health()
    assert result.status == "ok"


@respx.mock
def test_health_connection_error(settings: Settings) -> None:
    respx.get("http://127.0.0.1:47733/v1/health").mock(side_effect=httpx.ConnectError("refused"))
    with FluidVoiceClient(settings) as client:
        with pytest.raises(FluidNotRunningError):
            client.health()


@respx.mock
def test_transcribe_path(settings: Settings, tmp_path: Path) -> None:
    media = tmp_path / "test.wav"
    media.write_bytes(b"fake")
    respx.post("http://127.0.0.1:47733/v1/transcribe").mock(
        return_value=httpx.Response(200, json={"text": "hello world"})
    )
    with FluidVoiceClient(settings) as client:
        text = client.transcribe_path(media)
    assert text == "hello world"


@respx.mock
def test_transcribe_error(settings: Settings, tmp_path: Path) -> None:
    media = tmp_path / "test.wav"
    media.write_bytes(b"fake")
    respx.post("http://127.0.0.1:47733/v1/transcribe").mock(
        return_value=httpx.Response(200, json={"error": "bad audio"})
    )
    with FluidVoiceClient(settings) as client:
        with pytest.raises(TranscribeError):
            client.transcribe_path(media)


@respx.mock
def test_history_list(settings: Settings) -> None:
    respx.get("http://127.0.0.1:47733/v1/history").mock(
        return_value=httpx.Response(
            200,
            json=[{"fileName": "a.mp4", "text": "hello", "timestamp": "2025-01-01"}],
        )
    )
    with FluidVoiceClient(settings) as client:
        entries = client.history(limit=10)
    assert len(entries) == 1
    assert entries[0].fileName == "a.mp4"


@respx.mock
def test_postprocess(settings: Settings) -> None:
    respx.post("http://127.0.0.1:47733/v1/postprocess").mock(
        return_value=httpx.Response(200, json={"text": "Enhanced text."})
    )
    with FluidVoiceClient(settings) as client:
        result = client.postprocess("raw text", mode="dictate")
    assert result == "Enhanced text."


@respx.mock
def test_dictionary_add_word(settings: Settings) -> None:
    route = respx.post("http://127.0.0.1:47733/v1/dictionary/custom-words").mock(
        return_value=httpx.Response(200, json={})
    )
    with FluidVoiceClient(settings) as client:
        client.add_custom_word("Kubernetes", "container platform")
    assert route.called


@respx.mock
def test_list_custom_words_fluid_schema(settings: Settings) -> None:
    respx.get("http://127.0.0.1:47733/v1/dictionary/custom-words").mock(
        return_value=httpx.Response(
            200,
            json={
                "count": 1,
                "items": [
                    {
                        "text": "FluidVoice",
                        "aliases": ["fluid voice"],
                        "weight": 10,
                    }
                ],
            },
        )
    )
    with FluidVoiceClient(settings) as client:
        words = client.list_custom_words(limit=5)
    assert len(words) == 1
    assert words[0].word == "FluidVoice"
    assert words[0].aliases == ["fluid voice"]


@respx.mock
def test_postprocess_no_ai_provider(settings: Settings) -> None:
    respx.post("http://127.0.0.1:47733/v1/postprocess").mock(
        return_value=httpx.Response(400, json={"error": "No verified AI provider selected"})
    )
    with FluidVoiceClient(settings) as client:
        try:
            client.postprocess("hello")
            raise AssertionError("expected APIError")
        except APIError as exc:
            assert "AI provider" in exc.message
            assert exc.hint is not None
