"""Typed errors and exit codes for the FluidVoice CLI."""

from __future__ import annotations

# Exit codes (documented in README)
EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_FLUID_NOT_RUNNING = 2
EXIT_FFMPEG_MISSING = 3
EXIT_PARTIAL_BATCH_FAILURE = 4


class FluidVoiceError(Exception):
    """Base error for FluidVoice CLI."""

    exit_code: int = EXIT_USER_ERROR

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


class FluidNotRunningError(FluidVoiceError):
    """Local API is unreachable."""

    exit_code = EXIT_FLUID_NOT_RUNNING

    def __init__(self, base_url: str) -> None:
        super().__init__(
            f"FluidVoice Local API is not reachable at {base_url}",
            hint=(
                "Open FluidVoice → Settings → Advanced → Local API → Enable\n"
                "Ensure FluidVoice is running on this Mac"
            ),
        )


class TranscribeError(FluidVoiceError):
    """Transcription request failed."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Transcription failed: {detail}")


class FFmpegMissingError(FluidVoiceError):
    """ffmpeg or ffprobe not found on PATH."""

    exit_code = EXIT_FFMPEG_MISSING

    def __init__(self, tool: str) -> None:
        super().__init__(
            f"{tool} not found on PATH",
            hint="Install ffmpeg: brew install ffmpeg",
        )


class APIError(FluidVoiceError):
    """Unexpected API response."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"API error {status_code}: {detail}")


class BatchPartialFailureError(FluidVoiceError):
    """One or more files failed during batch processing."""

    exit_code = EXIT_PARTIAL_BATCH_FAILURE

    def __init__(self, failed: int, total: int) -> None:
        super().__init__(f"Batch completed with {failed}/{total} failures")
