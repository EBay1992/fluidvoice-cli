"""Media utilities: ffprobe duration and ffmpeg chunking."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from fluidvoice_cli.errors import FFmpegMissingError


def require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise FFmpegMissingError("ffmpeg")
    return path


def require_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise FFmpegMissingError("ffprobe")
    return path


def probe_duration(path: Path) -> float:
    """Return media duration in seconds."""
    require_ffprobe()
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
        return float(out)
    except (subprocess.CalledProcessError, ValueError) as exc:
        raise FFmpegMissingError("ffprobe") from exc


def chunk_audio(video: Path, workdir: Path, *, chunk_seconds: int) -> list[Path]:
    """Split audio into WAV chunks suitable for FluidVoice."""
    require_ffmpeg()
    pattern = workdir / "chunk_%03d.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "-f",
            "segment",
            "-segment_time",
            str(chunk_seconds),
            str(pattern),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return sorted(workdir.glob("chunk_*.wav"))


def transcribe_with_chunking(
    path: Path,
    transcribe_fn,
    *,
    chunk_seconds: int,
    max_direct_seconds: float,
    on_chunk: Callable[[int, int], None] | None = None,
) -> str:
    """Transcribe directly or via chunked WAV segments."""
    duration = probe_duration(path)
    if duration <= max_direct_seconds:
        return transcribe_fn(path)

    with tempfile.TemporaryDirectory(prefix="fluidvoice_chunks_") as tmp:
        chunks = chunk_audio(path, Path(tmp), chunk_seconds=chunk_seconds)
        parts: list[str] = []
        for i, chunk in enumerate(chunks, 1):
            if on_chunk:
                on_chunk(i, len(chunks))
            parts.append(transcribe_fn(chunk))
        return " ".join(parts)
