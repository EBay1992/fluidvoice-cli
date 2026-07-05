"""Media utility tests."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from fluidvoice_cli.errors import FFmpegMissingError
from fluidvoice_cli.media import probe_duration, require_ffprobe


@pytest.mark.skipif(shutil.which("ffprobe") is None, reason="ffprobe not installed")
def test_probe_duration_on_silent_wav(tmp_path: Path) -> None:
  # minimal valid WAV header + 1 second silence at 16kHz mono
    wav = tmp_path / "silent.wav"
    import wave

    with wave.open(str(wav), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)

    duration = probe_duration(wav)
    assert 0.9 <= duration <= 1.1


def test_require_ffprobe_missing() -> None:
    with patch("fluidvoice_cli.media.shutil.which", return_value=None):
        with pytest.raises(FFmpegMissingError):
            require_ffprobe()
