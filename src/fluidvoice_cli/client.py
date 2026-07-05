"""HTTP client for the FluidVoice Local API."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel

from fluidvoice_cli.config import Settings
from fluidvoice_cli.errors import APIError, FluidNotRunningError, TranscribeError


class HealthResponse(BaseModel):
    status: str


class TranscribeResponse(BaseModel):
    text: str = ""
    error: str | None = None


class HistoryEntry(BaseModel):
    fileName: str | None = None
    text: str = ""
    timestamp: str | None = None

    model_config = {"extra": "allow"}


class PostprocessResponse(BaseModel):
    text: str = ""
    error: str | None = None

    model_config = {"extra": "allow"}


class DictionaryWord(BaseModel):
    word: str
    definition: str | None = None

    model_config = {"extra": "allow"}


class ReplacementRule(BaseModel):
    original: str | None = None
    replacement: str | None = None

    model_config = {"extra": "allow"}


class FluidVoiceClient:
    """Typed client for FluidVoice Local API v1."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._client = httpx.Client(
            base_url=self.settings.base_url,
            timeout=httpx.Timeout(self.settings.timeout_seconds, connect=10.0),
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> FluidVoiceClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._client.request(method, path, json=json, params=params)
        except httpx.ConnectError as exc:
            raise FluidNotRunningError(self.settings.base_url) from exc
        except httpx.TimeoutException as exc:
            raise TranscribeError("request timed out") from exc

        if response.status_code >= 400:
            detail = response.text[:500] if response.text else response.reason_phrase
            raise APIError(response.status_code, detail or "unknown error")

        if not response.content:
            return {}
        return response.json()

    def health(self) -> HealthResponse:
        data = self._request("GET", "/health")
        return HealthResponse.model_validate(data)

    def transcribe_path(self, path: Path) -> str:
        """Transcribe via file path (FluidVoice convenience endpoint)."""
        data = self._request("POST", "/transcribe", json={"path": str(path.resolve())})
        result = TranscribeResponse.model_validate(data)
        if result.error and not result.text:
            raise TranscribeError(result.error)
        return result.text.strip()

    def transcribe_audio(self, audio_path: Path, audio_format: str = "wav") -> str:
        """Transcribe via base64 audio payload (documented API)."""
        raw = audio_path.read_bytes()
        payload = {
            "audio": base64.b64encode(raw).decode("ascii"),
            "format": audio_format,
        }
        data = self._request("POST", "/transcribe", json=payload)
        result = TranscribeResponse.model_validate(data)
        if result.error and not result.text:
            raise TranscribeError(result.error)
        return result.text.strip()

    def transcribe(self, path: Path) -> str:
        """Transcribe a file, preferring path-based API with base64 fallback."""
        try:
            return self.transcribe_path(path)
        except APIError:
            suffix = path.suffix.lstrip(".").lower() or "wav"
            return self.transcribe_audio(path, suffix)

    def history(self, *, limit: int = 50, offset: int = 0) -> list[HistoryEntry]:
        data = self._request("GET", "/history", params={"limit": limit, "offset": offset})
        if isinstance(data, list):
            return [HistoryEntry.model_validate(item) for item in data]
        if isinstance(data, dict) and "items" in data:
            return [HistoryEntry.model_validate(item) for item in data["items"]]
        return []

    def postprocess(
        self,
        text: str,
        *,
        mode: Literal["dictate", "edit"] = "dictate",
        context: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {"text": text, "mode": mode}
        if context is not None:
            payload["context"] = context
        data = self._request("POST", "/postprocess", json=payload)
        result = PostprocessResponse.model_validate(data)
        if result.error and not result.text:
            raise APIError(500, result.error)
        return result.text.strip()

    def list_custom_words(self, *, limit: int = 100) -> list[DictionaryWord]:
        data = self._request("GET", "/dictionary/custom-words", params={"limit": limit})
        items = data if isinstance(data, list) else data.get("words", data.get("items", []))
        return [DictionaryWord.model_validate(item) for item in items]

    def add_custom_word(self, word: str, definition: str | None = None) -> None:
        payload: dict[str, str] = {"word": word}
        if definition:
            payload["definition"] = definition
        self._request("POST", "/dictionary/custom-words", json=payload)

    def list_replacements(self, *, limit: int = 100) -> list[ReplacementRule]:
        data = self._request("GET", "/dictionary/replacements", params={"limit": limit})
        items = data if isinstance(data, list) else data.get("replacements", data.get("items", []))
        return [ReplacementRule.model_validate(item) for item in items]

    def add_replacement(self, original: str, replacement: str) -> None:
        self._request(
            "POST",
            "/dictionary/replacements",
            json={"original": original, "replacement": replacement},
        )
