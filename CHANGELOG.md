## [0.1.1] - 2026-07-05

### Fixed

- GitHub Actions CI workflow (correct repo root paths)

### Added

- Success messages after transcribe and batch jobs
- Default output: `.txt` beside source file with same name
- `--stdout` flag to print transcript instead of saving

## [0.1.0] - 2026-07-05

### Added

- Initial release: `health`, `doctor`, `transcribe`, `batch` commands
- `history list` and `history export`
- `postprocess` and `dict` subcommands
- `config show`
- Typed httpx client for FluidVoice Local API v1
- ffmpeg chunking for long media files
- History cache via API + plist fallback
- `--json` output mode for CI
- Exit codes for scripting
- TOML and environment configuration
