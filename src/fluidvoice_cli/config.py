"""Configuration with CLI > env > TOML > defaults precedence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "fluidvoice"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with path.open("rb") as f:
        return tomllib.load(f)


class Settings(BaseSettings):
    """FluidVoice CLI settings."""

    model_config = SettingsConfigDict(
        env_prefix="FLUIDVOICE_",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 47733
    timeout_seconds: float = 3600.0
    chunk_seconds: int = 240
    max_direct_seconds: float = 280.0
    skip_existing_min_bytes: int = 100
    history_limit: int = 500

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/v1"

    def with_overrides(self, **kwargs: object) -> Settings:
        data = self.model_dump()
        for key, value in kwargs.items():
            if value is not None and key in data:
                data[key] = value
        return Settings(**data)


def load_settings(config_file: Path | None = None) -> Settings:
    """Load settings from optional TOML file and environment."""
    path = config_file or DEFAULT_CONFIG_FILE
    if path.is_file():
        toml_data = _read_toml(path)
        flat = toml_data.get("fluidvoice", toml_data)
        return Settings(**flat)
    return Settings()
